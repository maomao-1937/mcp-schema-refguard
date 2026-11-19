#!/usr/bin/env python3
"""Offline JSON Schema reference scan for captured MCP tool schemas."""
import json
import sys
from urllib.parse import unquote

MAX_BYTES = 256 * 1024
MAX_DEPTH = 64
MAX_SCHEMAS = 256
MAX_REF_LENGTH = 2048


class InputError(Exception):
    pass


def pairs_no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError("duplicate_json_key")
        result[key] = value
    return result


def check_depth(value, depth=0):
    if depth > MAX_DEPTH:
        raise InputError("maximum_depth_exceeded")
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise InputError("object_key_must_be_string")
            check_depth(child, depth + 1)
    elif isinstance(value, list):
        for child in value:
            check_depth(child, depth + 1)


def pointer_exists(root, fragment):
    if fragment == "":
        return True
    if not fragment.startswith("/"):
        return None  # anchor, handled separately
    current = root
    for raw in fragment[1:].split("/"):
        if "~" in raw and any(token not in ("~0", "~1") for token in __import__("re").findall(r"~.", raw)):
            return False
        part = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and (part == "0" or not part.startswith("0")):
            index = int(part)
            if index >= len(current):
                return False
            current = current[index]
        else:
            return False
    return True


def audit_schema(root):
    issues = []
    anchors = set()

    def collect(value):
        if isinstance(value, dict):
            for key in ("$anchor", "$dynamicAnchor"):
                if isinstance(value.get(key), str):
                    anchors.add(value[key])
            for child in value.values():
                collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)

    collect(root)

    def visit(value, pointer=""):
        if isinstance(value, dict):
            for keyword in ("$ref", "$dynamicRef"):
                if keyword not in value:
                    continue
                ref = value[keyword]
                issue = None
                if not isinstance(ref, str) or not ref or len(ref) > MAX_REF_LENGTH:
                    issue = "invalid_reference_value"
                elif not ref.startswith("#"):
                    issue = "external_reference_blocked"
                else:
                    fragment = unquote(ref[1:])
                    exists = pointer_exists(root, fragment)
                    if exists is False:
                        issue = "unresolved_local_pointer"
                    elif exists is None and fragment not in anchors:
                        issue = "unresolved_local_anchor"
                if issue:
                    issues.append({"code": issue, "keyword": keyword, "pointer": pointer + "/" + keyword})
            for key, child in value.items():
                if key in ("$anchor", "$dynamicAnchor") and isinstance(child, str) and len(child) > 256:
                    issues.append({"code": "anchor_too_long", "keyword": key, "pointer": pointer + "/" + key})
                visit(child, pointer + "/" + key.replace("~", "~0").replace("/", "~1"))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, pointer + "/" + str(index))

    visit(root)
    issues.sort(key=lambda row: (row["pointer"], row["code"]))
    return issues


def inspect(document):
    if not isinstance(document, dict) or set(document) != {"schemas"}:
        raise InputError("top_level_keys_must_be_schemas")
    schemas = document["schemas"]
    if not isinstance(schemas, list) or len(schemas) > MAX_SCHEMAS:
        raise InputError("schemas_must_be_bounded_array")
    all_issues = []
    for ordinal, row in enumerate(schemas, 1):
        if not isinstance(row, dict) or set(row) != {"label", "schema"}:
            raise InputError("schema_entry_shape_invalid")
        if not isinstance(row["label"], str) or not row["label"] or len(row["label"]) > 128:
            raise InputError("schema_label_invalid")
        if not isinstance(row["schema"], dict):
            raise InputError("schema_must_be_object")
        for issue in audit_schema(row["schema"]):
            all_issues.append({"schema": ordinal, **issue})
    return {"ok": not all_issues, "schema_count": len(schemas), "issues": all_issues}


def main():
    if sys.argv[1:] in (["--help"], ["-h"]):
        print("usage: mcp_schema_refguard.py < input.json")
        return 0
    if sys.argv[1:]:
        return fail("arguments_not_supported")
    raw = sys.stdin.buffer.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        return fail("input_too_large")
    try:
        document = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs_no_duplicates)
        check_depth(document)
        result = inspect(document)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return fail("invalid_json")
    except InputError as exc:
        return fail(str(exc))
    except RecursionError:
        return fail("maximum_depth_exceeded")
    sys.stdout.write(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    return 0 if result["ok"] else 1


def fail(code):
    sys.stdout.write(json.dumps({"error": code}, sort_keys=True, separators=(",", ":")) + "\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
