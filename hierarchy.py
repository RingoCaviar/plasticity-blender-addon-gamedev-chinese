def filter_items_with_ancestors(add_items, update_items, item_ids, group_type=5, item_types=(0, 1)):
    """Keep requested mesh items and the complete group chain needed to link them."""
    item_ids = set(item_ids)
    item_types = set(item_types)
    ordered_items = list(add_items) + list(update_items)

    groups = {
        item.get("id"): item
        for item in ordered_items
        if item.get("type") == group_type and item.get("id") is not None
    }
    required_group_ids = set()
    for item in ordered_items:
        if item.get("type") not in item_types or item.get("id") not in item_ids:
            continue

        parent_id = item.get("parent_id", 0)
        visited = set()
        while parent_id and parent_id not in visited:
            visited.add(parent_id)
            parent = groups.get(parent_id)
            if parent is None:
                break
            required_group_ids.add(parent_id)
            parent_id = parent.get("parent_id", 0)

    def include(item):
        object_type = item.get("type")
        object_id = item.get("id")
        if object_type == group_type:
            return object_id in required_group_ids
        return object_type in item_types and object_id in item_ids

    return (
        [item for item in add_items if include(item)],
        [item for item in update_items if include(item)],
    )
