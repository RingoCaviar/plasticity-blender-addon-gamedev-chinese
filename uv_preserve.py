"""Preserve UV seams and coordinates across Plasticity mesh replacement.

Capture boundary seam states by adjacent CAD-face ID pairs and reapply
them after refresh or refacet. Transfer UV layers through face-ID-scoped
surface lookup.

Seams entirely inside a single CAD face, including manual and cylinder
cuts, are not restored. Affected faces are listed and selectable for repair.
"""

import traceback

import bpy
import numpy as np
from mathutils.bvhtree import BVHTree

# Visible state on the OBJECT (survives the mesh swap and .blend reload).
PAIRS_PROP = "plasticity_uv_seam_pairs"          # flat [idA, idB, seam, ...]
AFFECTED_PROP = "plasticity_uv_seam_affected"    # face ids needing attention


def _seams_enabled():
    scene = getattr(bpy.context, "scene", None)
    return bool(getattr(scene, "prop_plasticity_preserve_uv_seams", True))


def _uvs_enabled():
    scene = getattr(bpy.context, "scene", None)
    return bool(getattr(scene, "prop_plasticity_preserve_uvs", True))


def _set_status(text):
    try:
        bpy.context.window_manager.plasticity_uv_preserve_status = text
    except Exception:
        pass


def _loop_face_ids(mesh):
    """Per-loop Plasticity face id (or None when the mesh carries no ids)."""
    groups = mesh.get("groups")
    face_ids = mesh.get("face_ids")
    if not groups or not face_ids:
        return None
    # Deferred (handler imports this module at top level), and via the
    # module path: the package attribute "handler" is shadowed by a
    # SceneHandler instance.
    from .handler import _build_loop_face_ids
    loop_ids = _build_loop_face_ids(
        mesh, [int(x) for x in groups], [int(x) for x in face_ids])
    if not loop_ids:
        return None
    return np.asarray(loop_ids, dtype=np.int64)


def _edge_tables(mesh, loop_ids):
    """Build boundary tables keyed by rounded vertex positions.

    Unwelded refresh meshes can represent a shared CAD boundary with
    separate edges and vertex indices. Position keys combine duplicates
    and also work for welded refacet meshes. Avoid loop.edge_index because
    it may not be initialized on a newly built mesh.

    Returns (key_fids, key_polys, key_edges): per position-key the set of
    adjacent CAD ids, the adjacent polygon count, and the list of physical
    edge indices (2 coincident copies on unwelded boundaries).
    """
    if len(mesh.edges) == 0 and len(mesh.polygons) > 0:
        mesh.update(calc_edges=True)

    coords = np.empty(len(mesh.vertices) * 3, dtype=np.float64)
    mesh.vertices.foreach_get("co", coords)
    coords = coords.reshape(-1, 3).round(6)
    vertex_keys = [tuple(row) for row in coords]

    edge_vertices = np.empty(len(mesh.edges) * 2, dtype=np.int32)
    mesh.edges.foreach_get("vertices", edge_vertices)
    key_edges = {}
    for edge_index in range(len(mesh.edges)):
        ka = vertex_keys[int(edge_vertices[edge_index * 2])]
        kb = vertex_keys[int(edge_vertices[edge_index * 2 + 1])]
        key = (ka, kb) if ka <= kb else (kb, ka)
        key_edges.setdefault(key, []).append(edge_index)

    loop_verts = np.empty(len(mesh.loops), dtype=np.int32)
    mesh.loops.foreach_get("vertex_index", loop_verts)
    loop_starts = np.empty(len(mesh.polygons), dtype=np.int32)
    loop_totals = np.empty(len(mesh.polygons), dtype=np.int32)
    mesh.polygons.foreach_get("loop_start", loop_starts)
    mesh.polygons.foreach_get("loop_total", loop_totals)

    key_fids = {}
    key_polys = {}
    for poly_index in range(len(mesh.polygons)):
        start = int(loop_starts[poly_index])
        total = int(loop_totals[poly_index])
        fid = int(loop_ids[start])
        if fid < 0:
            continue
        for corner in range(total):
            ka = vertex_keys[int(loop_verts[start + corner])]
            kb = vertex_keys[int(loop_verts[start + (corner + 1) % total])]
            key = (ka, kb) if ka <= kb else (kb, ka)
            key_fids.setdefault(key, set()).add(fid)
            key_polys[key] = key_polys.get(key, 0) + 1
    return key_fids, key_polys, key_edges


def capture(mesh):
    """Snapshot the seam state keyed by stable face-ID pairs.

    Returns a state dict, or None when the mesh has no Plasticity ids.
    """
    loop_ids = _loop_face_ids(mesh)
    if loop_ids is None:
        return None
    key_fids, key_polys, key_edges = _edge_tables(mesh, loop_ids)

    seams = np.zeros(len(mesh.edges), dtype=bool)
    mesh.edges.foreach_get("use_seam", seams)

    boundary_votes = {}   # (a, b) -> [seam_edges, total_edges]
    internal_faces = set()
    for key, fids in key_fids.items():
        edge_indices = key_edges.get(key, [])
        has_seam = any(seams[e] for e in edge_indices)
        if len(fids) == 2:
            pair = tuple(sorted(fids))
            votes = boundary_votes.setdefault(pair, [0, 0])
            votes[1] += 1
            if has_seam:
                votes[0] += 1
        elif (len(fids) == 1 and has_seam
              and key_polys.get(key, 0) >= 2):
            # Interior edge of one CAD face carrying a seam: a mid-face cut
            # (manual or auto cylinder) — restore is parked; report it.
            internal_faces.add(next(iter(fids)))

    pairs = {}
    mixed = []
    for key, (seam_edges, total_edges) in boundary_votes.items():
        pairs[key] = seam_edges * 2 >= total_edges
        if 0 < seam_edges < total_edges:
            mixed.append(key)

    return {
        "pairs": pairs,
        "mixed": mixed,
        "internal_faces": sorted(internal_faces),
        "ids": {int(x) for x in np.unique(loop_ids) if int(x) >= 0},
    }


def apply(mesh, state):
    """Reapply a captured seam map onto the (new) mesh. Returns a report."""
    loop_ids = _loop_face_ids(mesh)
    if loop_ids is None:
        return None
    key_fids, _key_polys, key_edges = _edge_tables(mesh, loop_ids)

    pairs = state["pairs"]
    # A brand-new adjacency has no recorded decision; follow the mesh's own
    # convention: split (seam) when the user's map contains any seams at
    # all, untouched otherwise (a never-marked mesh stays never-marked).
    default_seam = any(pairs.values())

    seams = np.zeros(len(mesh.edges), dtype=bool)
    mesh.edges.foreach_get("use_seam", seams)

    applied_pairs = set()
    new_pairs = set()
    for key, fids in key_fids.items():
        if len(fids) != 2:
            continue
        pair = tuple(sorted(fids))
        if pair in pairs:
            value = pairs[pair]
            applied_pairs.add(pair)
        else:
            value = default_seam
            new_pairs.add(pair)
        for edge_index in key_edges.get(key, []):
            seams[edge_index] = value
    mesh.edges.foreach_set("use_seam", seams)
    mesh["plasticity_seams_version"] = int(
        mesh.get("plasticity_seams_version", 0)) + 1

    new_ids = {int(x) for x in np.unique(loop_ids) if int(x) >= 0}
    lost_ids = sorted(state["ids"] - new_ids)
    new_face_ids = sorted(new_ids - state["ids"])
    # Select faces needing repair: mid-face cuts and new faces without
    # recorded seam state. Removed faces can only be reported by ID.
    affected = sorted(set(state["internal_faces"]) | set(new_face_ids))
    return {
        "applied": len(applied_pairs),
        "known": len(pairs),
        "new_pairs": sorted(new_pairs),
        "lost_ids": lost_ids,
        "new_face_ids": new_face_ids,
        "internal_faces": state["internal_faces"],
        "affected": affected,
    }


def _transfer_corner_layers(old_mesh, new_mesh, new_loop_ids):
    """Copy per-corner UV layers old -> new by ID-scoped surface lookup.

    For every new polygon: nearest old triangle OF THE SAME CAD FACE
    (per-ID BVH trees make cross-boundary bleeding impossible), then each
    corner interpolates the old triangle's corner values barycentrically.
    The reference triangle is chosen from the polygon CENTER so all
    corners of one polygon read the same side of any mid-face seam.
    Planar faces transfer exactly; curved ones within facet tolerance.

    Returns (layer_count, missing_ids).
    """
    if not old_mesh.uv_layers:
        return 0, set()
    old_loop_ids = _loop_face_ids(old_mesh)
    if old_loop_ids is None:
        return 0, set()

    old_mesh.calc_loop_triangles()
    old_coords = np.empty(len(old_mesh.vertices) * 3, dtype=np.float64)
    old_mesh.vertices.foreach_get("co", old_coords)
    old_coords = old_coords.reshape(-1, 3)

    tris_by_fid = {}
    for tri in old_mesh.loop_triangles:
        fid = int(old_loop_ids[tri.loops[0]])
        if fid < 0:
            continue
        tris_by_fid.setdefault(fid, []).append(tri)

    vertex_list = [tuple(row) for row in old_coords]
    bvh_by_fid = {
        fid: BVHTree.FromPolygons(
            vertex_list, [tuple(tri.vertices) for tri in tris],
            all_triangles=True)
        for fid, tris in tris_by_fid.items()
    }

    # Old layer data as arrays: (layer, loop, 2)
    layer_names = [layer.name for layer in old_mesh.uv_layers]
    old_layer_data = []
    for layer in old_mesh.uv_layers:
        data = np.empty(len(old_mesh.loops) * 2, dtype=np.float64)
        layer.data.foreach_get("uv", data)
        old_layer_data.append(data.reshape(-1, 2))

    new_layers = []
    for name in layer_names:
        layer = new_mesh.uv_layers.get(name)
        if layer is None:
            layer = new_mesh.uv_layers.new(name=name, do_init=False)
        new_layers.append(layer)

    new_coords = np.empty(len(new_mesh.vertices) * 3, dtype=np.float64)
    new_mesh.vertices.foreach_get("co", new_coords)
    new_coords = new_coords.reshape(-1, 3)
    loop_verts = np.empty(len(new_mesh.loops), dtype=np.int32)
    new_mesh.loops.foreach_get("vertex_index", loop_verts)
    loop_starts = np.empty(len(new_mesh.polygons), dtype=np.int32)
    loop_totals = np.empty(len(new_mesh.polygons), dtype=np.int32)
    centers = np.empty(len(new_mesh.polygons) * 3, dtype=np.float64)
    new_mesh.polygons.foreach_get("loop_start", loop_starts)
    new_mesh.polygons.foreach_get("loop_total", loop_totals)
    new_mesh.polygons.foreach_get("center", centers)
    centers = centers.reshape(-1, 3)

    out = [np.zeros((len(new_mesh.loops), 2), dtype=np.float64)
           for _ in layer_names]
    missing_ids = set()
    for poly_index in range(len(new_mesh.polygons)):
        start = int(loop_starts[poly_index])
        total = int(loop_totals[poly_index])
        fid = int(new_loop_ids[start])
        bvh = bvh_by_fid.get(fid)
        if bvh is None:
            if fid >= 0:
                missing_ids.add(fid)
            continue
        hit = bvh.find_nearest(centers[poly_index])
        if hit is None or hit[2] is None:
            missing_ids.add(fid)
            continue
        tri = tris_by_fid[fid][hit[2]]
        tri_loops = tri.loops
        vert_a = old_coords[tri.vertices[0]]
        edge_1 = old_coords[tri.vertices[1]] - vert_a
        edge_2 = old_coords[tri.vertices[2]] - vert_a
        d11 = edge_1 @ edge_1
        d12 = edge_1 @ edge_2
        d22 = edge_2 @ edge_2
        det = d11 * d22 - d12 * d12
        if abs(det) < 1e-20:
            continue
        for corner in range(total):
            loop_index = start + corner
            # Affine barycentric weights (projected onto the triangle's
            # plane, extrapolating linearly outside it) — mean-value
            # weights are NOT affine outside the triangle and skew UVs
            # when a corner falls in a neighboring old triangle.
            rel = new_coords[loop_verts[loop_index]] - vert_a
            r1 = rel @ edge_1
            r2 = rel @ edge_2
            s = (d22 * r1 - d12 * r2) / det
            t = (d11 * r2 - d12 * r1) / det
            w0 = 1.0 - s - t
            for layer_index, data in enumerate(old_layer_data):
                out[layer_index][loop_index] = (
                    w0 * data[tri_loops[0]]
                    + s * data[tri_loops[1]]
                    + t * data[tri_loops[2]])

    for layer_index, layer in enumerate(new_layers):
        layer.data.foreach_set("uv", out[layer_index].ravel())
    return len(new_layers), missing_ids


def store_state(obj, state):
    flat = []
    for (id_a, id_b), seam in sorted(state["pairs"].items()):
        flat.extend((int(id_a), int(id_b), int(seam)))
    obj[PAIRS_PROP] = flat


def load_stored_pairs(obj):
    flat = [int(x) for x in obj.get(PAIRS_PROP, [])]
    return {(flat[i], flat[i + 1]): bool(flat[i + 2])
            for i in range(0, len(flat) - 2, 3)}


def capture_before_update(obj):
    """Handler hook: snapshot the old mesh right before it is replaced.

    Stored object state preserves boundary pairs absent from a temporary
    or unwelded mesh. Fresh observations override stored pairs, and pairs
    for removed CAD faces are pruned.
    """
    if not (_seams_enabled() or _uvs_enabled()):
        return None
    try:
        state = capture(obj.data)
    except Exception:
        print("[uv_preserve] capture failed for %r:\n%s"
              % (obj.name, traceback.format_exc()))
        return None
    if state is None:
        return None
    try:
        merged = load_stored_pairs(obj)
        merged = {pair: seam for pair, seam in merged.items()
                  if pair[0] in state["ids"] and pair[1] in state["ids"]}
        merged.update(state["pairs"])
        state["pairs"] = merged
        store_state(obj, state)
    except Exception:
        pass

    state["snapshot"] = None
    if _uvs_enabled() and obj.data.uv_layers:
        try:
            snapshot = obj.data.copy()
            snapshot.name = "__uvp_snap_" + obj.name
            state["snapshot"] = snapshot
        except Exception:
            print("[uv_preserve] snapshot failed for %r:\n%s"
                  % (obj.name, traceback.format_exc()))
    return state


def _keep_backup(obj, snapshot):
    """A failed transfer must never consume the user's data: keep the old
    mesh in the file, visibly named, and say so."""
    try:
        snapshot.name = obj.name + "_uv_backup"
        snapshot.use_fake_user = True
    except Exception:
        pass


def restore_after_update(obj, state):
    """Handler hook: reapply seams + UVs onto the freshly rebuilt mesh."""
    if state is None:
        return
    snapshot = state.get("snapshot")
    if not state["pairs"] and snapshot is None:
        return

    report = None
    if state["pairs"]:
        try:
            report = apply(obj.data, state)
        except Exception:
            print("[uv_preserve] seam restore failed for %r:\n%s"
                  % (obj.name, traceback.format_exc()))

    uv_note = ""
    affected_extra = set()
    if snapshot is not None:
        try:
            new_loop_ids = _loop_face_ids(obj.data)
            if new_loop_ids is None:
                raise RuntimeError("new mesh carries no face ids")
            layer_count, missing_ids = _transfer_corner_layers(
                snapshot, obj.data, new_loop_ids)
            affected_extra = {int(x) for x in missing_ids}
            uv_note = " · UVs restored" if layer_count else ""
            bpy.data.meshes.remove(snapshot)
        except Exception:
            print("[uv_preserve] UV transfer failed for %r:\n%s"
                  % (obj.name, traceback.format_exc()))
            _keep_backup(obj, snapshot)
            uv_note = " · UVs NOT restored (backup mesh kept)"

    if report is None and not uv_note:
        return
    affected = set(report["affected"]) if report else set()
    affected |= affected_extra
    try:
        obj[AFFECTED_PROP] = sorted(int(x) for x in affected)
    except Exception:
        pass

    parts = []
    if report is not None:
        parts.append(
            f"{report['applied']}/{report['known']} boundaries restored")
        if report["new_pairs"]:
            parts.append(f"{len(report['new_pairs'])} new boundaries")
        if report["lost_ids"]:
            parts.append(f"{len(report['lost_ids'])} faces gone (model edit)")
        if report["internal_faces"]:
            parts.append(
                f"{len(report['internal_faces'])} faces need internal re-cut")
    if affected_extra:
        parts.append(f"{len(affected_extra)} new faces need unwrap")
    message = ("UV seams: " + obj.name + ": " + " · ".join(parts)
               + uv_note if parts else "UV: " + obj.name + uv_note)
    print("[uv_preserve] " + message)
    _set_status(message)

    try:
        from . import operators
        operators._invalidate_live_expand_overlay_cache()
    except Exception:
        pass


class PLASTICITY_OT_select_uv_seam_affected(bpy.types.Operator):
    bl_idname = "plasticity.select_uv_seam_affected"
    bl_label = "Select Faces To Fix"
    bl_description = (
        "Select the faces that need manual UV work after the last "
        "Plasticity update (re-cut a mid-face seam, or re-unwrap faces "
        "that were changed in Plasticity)"
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None and obj.type == 'MESH'
                and AFFECTED_PROP in obj.keys())

    def execute(self, context):
        obj = context.active_object
        affected = {int(x) for x in obj.get(AFFECTED_PROP, [])}
        if not affected:
            self.report({'INFO'}, "Nothing needs attention on this object")
            return {'CANCELLED'}
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        mesh = obj.data
        loop_ids = _loop_face_ids(mesh)
        if loop_ids is None:
            self.report({'ERROR'}, "Mesh carries no Plasticity face ids")
            return {'CANCELLED'}
        loop_starts = np.empty(len(mesh.polygons), dtype=np.int32)
        mesh.polygons.foreach_get("loop_start", loop_starts)
        poly_ids = loop_ids[loop_starts]
        selection = np.isin(poly_ids, sorted(affected))

        mesh.polygons.foreach_set("select", selection)
        mesh.vertices.foreach_set(
            "select", np.zeros(len(mesh.vertices), dtype=bool))
        mesh.edges.foreach_set(
            "select", np.zeros(len(mesh.edges), dtype=bool))
        bpy.ops.object.mode_set(mode='EDIT')
        context.tool_settings.mesh_select_mode = (False, False, True)
        count = int(selection.sum())
        self.report({'INFO'}, f"Selected {count} faces needing attention")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(PLASTICITY_OT_select_uv_seam_affected)
    bpy.types.Scene.prop_plasticity_preserve_uv_seams = bpy.props.BoolProperty(
        name="Preserve UV Seams",
        description="Keep your seams and merged islands when the mesh is "
                    "updated from Plasticity (Refresh or Refacet)",
        default=True,
    )
    bpy.types.Scene.prop_plasticity_preserve_uvs = bpy.props.BoolProperty(
        name="Preserve UVs",
        description="Keep your UVs when the mesh is updated from "
                    "Plasticity, so textures and masks stay aligned",
        default=True,
    )
    bpy.types.WindowManager.plasticity_uv_preserve_status = bpy.props.StringProperty(
        name="UV preserve status", default="", options={'HIDDEN'})


def unregister():
    del bpy.types.WindowManager.plasticity_uv_preserve_status
    del bpy.types.Scene.prop_plasticity_preserve_uvs
    del bpy.types.Scene.prop_plasticity_preserve_uv_seams
    bpy.utils.unregister_class(PLASTICITY_OT_select_uv_seam_affected)
