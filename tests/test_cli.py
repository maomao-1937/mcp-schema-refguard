import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "mcp_schema_refguard.py"


def run(document):
    return subprocess.run([sys.executable, str(SCRIPT)], input=document, text=True,
                          capture_output=True, cwd=ROOT, timeout=5)


class RefguardTests(unittest.TestCase):
    def test_local_pointer_exact_example(self):
        doc = '{"schemas":[{"label":"tool output","schema":{"$defs":{"x":{"type":"string"}},"properties":{"x":{"$ref":"#/$defs/x"}}}}]}'
        result = run(doc)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '{"issues":[],"ok":true,"schema_count":1}\n')

    def test_external_reference_blocked_without_echo(self):
        result = run('{"schemas":[{"label":"safe","schema":{"$ref":"https://example.invalid/schema"}}]}')
        self.assertEqual(result.returncode, 1)
        self.assertIn('"code":"external_reference_blocked"', result.stdout)
        self.assertNotIn("example.invalid", result.stdout)

    def test_file_uri_blocked(self):
        result = run('{"schemas":[{"label":"s","schema":{"$ref":"file:///etc/passwd"}}]}')
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("passwd", result.stdout)

    def test_unresolved_pointer_detected(self):
        result = run('{"schemas":[{"label":"s","schema":{"$ref":"#/missing"}}]}')
        self.assertIn('"code":"unresolved_local_pointer"', result.stdout)

    def test_anchor_resolves(self):
        result = run('{"schemas":[{"label":"s","schema":{"$anchor":"item","properties":{"x":{"$ref":"#item"}}}}]}')
        self.assertEqual(result.returncode, 0)

    def test_duplicate_json_keys_rejected(self):
        result = run('{"schemas":[],"schemas":[]}')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, '{"error":"duplicate_json_key"}\n')

    def test_non_object_schema_rejected(self):
        result = run('{"schemas":[{"label":"s","schema":[]}]}')
        self.assertEqual(result.returncode, 2)

    def test_size_cap(self):
        result = run(' ' * (256 * 1024 + 1))
        self.assertEqual(result.stdout, '{"error":"input_too_large"}\n')


if __name__ == "__main__":
    unittest.main()
