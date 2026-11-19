# mcp-schema-refguard

Scan captured MCP tool schemas for external or unresolved JSON Schema references without fetching anything.

For MCP client and server developers reviewing captured tools/list metadata.

## Quick start

Requires Python 3.11 or newer. There are no third-party dependencies. The CLI reads one JSON document from standard input and writes one deterministic JSON line.

```console
python mcp_schema_refguard.py < examples/input.json
```

Output:

```json
{"issues":[],"ok":true,"schema_count":1}
```

To run the tests and the exact example check:

```console
python -m unittest discover -s tests -v
python examples/run_examples.py
```

Inputs are limited to 256 KiB; malformed, duplicate-key, or over-depth JSON fails with a fixed error code. Output avoids echoing schema descriptions and values; issue pointers can include schema object keys. No MCP server is started or contacted.

## Problem evidence and scope

The MCP Python SDK advisory GHSA-rwrf-2pqf-9j8j reports affected client versions fetched server-selected HTTP, HTTPS, or file references during output-schema validation. The tool is a preventive offline scanner, not a reproduction of the vulnerability.

This evidence describes specific reports and documented behavior. It does not establish how often the problem occurs or predict GitHub stars.

## Limits

Supports local JSON Pointer references and declared anchors for existence checks. It does not implement full JSON Schema resolution, validate schema semantics, or fetch any reference.

## License and attribution

MIT. This repository contains original code and synthetic fixtures; no upstream source code or assets are included.

## Verified environment

Python 3.11.15 on Windows and GitHub Actions on Ubuntu and Windows using Python 3.11.
