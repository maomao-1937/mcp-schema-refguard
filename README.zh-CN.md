# mcp-schema-refguard

扫描 MCP 工具 schema 快照中的外部引用和无法解析的本地引用；整个过程不联网、不读取本地文件。

适用对象：检查 tools/list 快照的 MCP 客户端和服务端开发者。

## 快速开始

需要 Python 3.11 或更新版本，无第三方依赖。CLI 从标准输入读取一份 JSON，并输出一行确定性 JSON。

```console
python mcp_schema_refguard.py < examples/input.json
```

输出：

```json
{"issues":[],"ok":true,"schema_count":1}
```

运行测试和精确示例检查：

```console
python -m unittest discover -s tests -v
python examples/run_examples.py
```

输入限制为 256 KiB；畸形 JSON、重复键或过深输入会返回固定错误码。输出不会回显 schema 描述或值，问题指针可能包含 schema 对象键名。程序不会启动或连接 MCP 服务。

## 问题证据与范围

MCP Python SDK 安全公告 GHSA-rwrf-2pqf-9j8j 说明受影响版本会在输出 schema 验证期间读取服务器提供的 HTTP、HTTPS 或 file 引用。本工具是离线预检器，不复现漏洞。

这些证据仅说明具体报告和公开记录的行为，不能证明问题发生频率，也不能预测 GitHub Star。

## 限制

仅检查本地 JSON Pointer 和已声明锚点是否存在；不实现完整 JSON Schema 解析，不验证 schema 语义，也不会获取任何引用目标。

## 许可证与署名

MIT。本仓库使用原创代码和合成样例，不包含上游代码或素材。

## 已验证环境

Windows Python 3.11.15；GitHub Actions Ubuntu 与 Windows，Python 3.11。
