import importlib
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
