# Research notes: mcp-schema-refguard

## Observed source facts

The MCP Python SDK advisory GHSA-rwrf-2pqf-9j8j reports affected client versions fetched server-selected HTTP, HTTPS, or file references during output-schema validation. The tool is a preventive offline scanner, not a reproduction of the vulnerability.

Sources:
- https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-rwrf-2pqf-9j8j
- https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/migration.md

## Selection judgment

Scan captured MCP tool schemas for external or unresolved JSON Schema references without fetching anything. This is a narrowly scoped offline utility derived from those observations. The sources do not establish prevalence, market size, or expected stars.
