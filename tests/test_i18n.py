"""Static checks for the translation catalog (no display, no libtorrent needed).

Run with:  python -m unittest discover -s tests -v
"""
import ast
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import i18n  # noqa: E402

PLACEHOLDER = re.compile(r"\{([A-Za-z_0-9]+)(?::[^{}]*)?\}")
TREE = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))


def tr_calls():
    for node in ast.walk(TREE):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "tr" and node.args:
            yield node


class CatalogTests(unittest.TestCase):
    def test_every_literal_tr_key_is_in_the_catalog(self):
        missing = [(n.lineno, n.args[0].value[:60]) for n in tr_calls()
                   if isinstance(n.args[0], ast.Constant) and n.args[0].value not in i18n.EN]
        self.assertEqual(missing, [], "tr() strings without an English translation")

    def test_placeholders_match_the_call_arguments(self):
        bad = []
        for n in tr_calls():
            a = n.args[0]
            if isinstance(a, ast.Constant):
                names = set(PLACEHOLDER.findall(a.value))
                kwargs = {k.arg for k in n.keywords}
                if names != kwargs:
                    bad.append((n.lineno, names, kwargs))
        self.assertEqual(bad, [])

    def test_translation_keeps_the_same_placeholders(self):
        bad = [k[:60] for k, v in i18n.EN.items() if set(PLACEHOLDER.findall(k)) != set(PLACEHOLDER.findall(v))]
        self.assertEqual(bad, [])

    def test_no_unused_catalog_entries(self):
        literals = {n.value for n in ast.walk(TREE) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
        unused = [k[:60] for k in i18n.EN if k not in literals]
        self.assertEqual(unused, [], "catalog entries that no longer exist in app.py")


class HelperTests(unittest.TestCase):
    def tearDown(self):
        i18n.set_language("pt")

    def test_portuguese_is_the_source_language(self):
        i18n.set_language("pt")
        self.assertEqual(i18n.tr("Fila"), "Fila")
        self.assertEqual(i18n.tr("{n} transferência{s} em curso", n=2, s=i18n.pl(2)), "2 transferências em curso")

    def test_english_translation_and_fallback(self):
        i18n.set_language("en")
        self.assertEqual(i18n.tr("Fila"), "Queue")
        self.assertEqual(i18n.tr("{n} transferência{s} em curso", n=1, s=i18n.pl(1)), "1 transfer in progress")
        self.assertEqual(i18n.tr("texto que não existe"), "texto que não existe")

    def test_unknown_language_falls_back_to_portuguese(self):
        i18n.set_language("xx")
        self.assertEqual(i18n.LANG, "pt")

    def test_resolve_language(self):
        self.assertEqual(i18n.resolve_language("en"), "en")
        self.assertIn(i18n.resolve_language("auto"), ("pt", "en"))


if __name__ == "__main__":
    unittest.main()
