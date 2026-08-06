import ast
import importlib
from pathlib import Path
import sys
import types
import unittest


class ReportTranslationTests(unittest.TestCase):
    def test_report_translates_before_forwarding_to_blender(self):
        fake_bpy = types.SimpleNamespace(
            app=types.SimpleNamespace(
                translations=types.SimpleNamespace(pgettext_iface=lambda text: "已翻译：" + text)
            )
        )
        sys.modules["bpy"] = fake_bpy
        try:
            import translations
            translations = importlib.reload(translations)
            receiver = types.SimpleNamespace(calls=[])
            receiver.report = lambda level, text: receiver.calls.append((level, text))
            translations.report(receiver, {"INFO"}, "Connected")
            self.assertEqual(receiver.calls, [({"INFO"}, "已翻译：Connected")])
        finally:
            sys.modules.pop("bpy", None)


class TranslationCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = Path(__file__).with_name("translations.py").read_text(encoding="utf-8")
        cls.catalog_tree = ast.parse(source)
        cls.catalog_nodes = [
            node.value
            for node in cls.catalog_tree.body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "_ZH" for target in node.targets)
        ]
        cls.catalog = ast.literal_eval(cls.catalog_nodes[0])

    @staticmethod
    def _literal_string(node):
        try:
            value = ast.literal_eval(node)
        except (ValueError, TypeError):
            return None
        return value if isinstance(value, str) else None

    def test_all_static_tooltips_and_enum_items_are_translated(self):
        missing = set()
        root = Path(__file__).parent
        for filename in ("__init__.py", "operators.py", "ui.py"):
            tree = ast.parse((root / filename).read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, (ast.Assign, ast.AnnAssign)):
                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                    if any(isinstance(target, ast.Name) and target.id == "bl_description" for target in targets):
                        text = self._literal_string(node.value)
                        if text and text not in self.catalog:
                            missing.add(text)

                if not isinstance(node, ast.Call):
                    continue
                for keyword in node.keywords:
                    if keyword.arg == "description":
                        text = self._literal_string(keyword.value)
                        if text and text not in self.catalog:
                            missing.add(text)
                    elif keyword.arg == "items":
                        try:
                            items = ast.literal_eval(keyword.value)
                        except (ValueError, TypeError):
                            continue
                        for item in items:
                            if not isinstance(item, (tuple, list)):
                                continue
                            for text in item[1:3]:
                                if isinstance(text, str) and text and text not in self.catalog:
                                    missing.add(text)

        self.assertEqual(missing, set(), f"Missing translations: {sorted(missing)}")

    def test_dynamic_checker_placeholder_is_translated(self):
        source = Path(__file__).with_name("operators.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        checker_function = next(
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "get_checker_image_items"
        )
        missing = set()
        for node in ast.walk(checker_function):
            if not isinstance(node, (ast.Tuple, ast.List)):
                continue
            try:
                item = ast.literal_eval(node)
            except (ValueError, TypeError):
                continue
            if not isinstance(item, (tuple, list)) or len(item) < 3:
                continue
            for text in item[1:3]:
                if isinstance(text, str) and text and text not in self.catalog:
                    missing.add(text)
        self.assertEqual(missing, set(), f"Missing dynamic enum translations: {sorted(missing)}")

    def test_translation_keys_are_unique(self):
        keys = [ast.literal_eval(key) for key in self.catalog_nodes[0].keys]
        duplicates = sorted({key for key in keys if keys.count(key) > 1})
        self.assertEqual(duplicates, [], f"Duplicate translation keys: {duplicates}")

    def test_operators_imports_translations_before_reporting(self):
        """Operator report calls must have the translations module bound at runtime."""
        source = Path(__file__).with_name("operators.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports_translations = any(
            isinstance(node, ast.ImportFrom)
            and any(alias.name == "translations" for alias in node.names)
            for node in tree.body
        )
        uses_translation_reports = any(
            isinstance(node, ast.Attribute)
            and node.attr == "report"
            and isinstance(node.value, ast.Name)
            and node.value.id == "translations"
            for node in ast.walk(tree)
        )
        self.assertFalse(
            uses_translation_reports and not imports_translations,
            "operators.py calls translations.report without importing translations",
        )

    def test_report_template_translates_before_formatting(self):
        fake_bpy = types.SimpleNamespace(
            app=types.SimpleNamespace(translations=types.SimpleNamespace(
                pgettext_iface=lambda text: "文件名：{filename}" if text == "Filename: {filename}" else text
            ))
        )
        sys.modules["bpy"] = fake_bpy
        try:
            import translations
            translations = importlib.reload(translations)
            receiver = types.SimpleNamespace(calls=[])
            receiver.report = lambda level, text: receiver.calls.append((level, text))
            translations.report_template(receiver, {"INFO"}, "Filename: {filename}", filename="part.psx")
            self.assertEqual(receiver.calls, [({"INFO"}, "文件名：part.psx")])
        finally:
            sys.modules.pop("bpy", None)


if __name__ == "__main__":
    unittest.main()
