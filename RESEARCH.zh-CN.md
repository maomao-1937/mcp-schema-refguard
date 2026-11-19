# 研究记录：mcp-schema-refguard

## 来源中可观察的事实

MCP Python SDK 安全公告 GHSA-rwrf-2pqf-9j8j 说明受影响版本会在输出 schema 验证期间读取服务器提供的 HTTP、HTTPS 或 file 引用。本工具是离线预检器，不复现漏洞。

来源链接见 [RESEARCH.md](RESEARCH.md)。

## 选题判断

扫描 MCP 工具 schema 快照中的外部引用和无法解析的本地引用；整个过程不联网、不读取本地文件。 这是基于上述观察形成的离线工具设想；来源不能证明发生率、市场规模或预期 Star。
