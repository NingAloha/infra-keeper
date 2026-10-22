# InfraKeeper

[English](README.md) | **简体中文**

InfraKeeper 是一个实验性的 **Agent Plugin**，封装了一份标准 **Agent Skill**，用于基于证据维护基础设施文档。

## 快速开始

1. 在兼容的 Agent Plugin 宿主中安装本仓库（见下文）。
2. 输入 **「初始化 InfraKeeper」** 或 **「Set up InfraKeeper」**。Skill 会启动只读的初始化向导。
3. 选择 **GitHub MCP**、**GitHub CLI（`gh`）** 或两者。无需两个后端都配置；一个可用即可，
   之后随时可以再添加第二个。
4. 告诉向导要使用的仓库（`OWNER/REPO`）。它会为每个后端给出一个判定：`ready`、`unavailable`、
   `unauthenticated`、`insufficient-permissions` 或 `unverified`。

向导是**只读的**。它不会创建测试提交或测试文件，也不会自行修改你的 MCP 配置、环境变量或凭据
文件。OAuth 授权、PAT 创建与 `gh auth login` 均由你本人完成；Skill 不会索取、显示或保存令牌。

初始化结束时会指向设备审计。该审计在**本版本中尚未实现**。

## 包结构

```text
README.md
README.zh-CN.md
plugin.json
skills/infra-keeper/SKILL.md
skills/infra-keeper/references/
  github-backends.md
  github-mcp.md
  github-cli.md
  github-workflow.md
  setup-wizard.md
docs/hermes.md
tests/
  hermes-smoke-test.md
  hermes-mcp-smoke-test.md
  integration/mcp-lifecycle.md
  integration/cli-lifecycle.md
```

插件打包面向 [Agent Plugins](https://agent-plugins.org/specification)；内嵌 Skill 遵循
[Agent Skills 规范](https://agentskills.io/specification)。各宿主的兼容性需分别验证。

## 安装与 GitHub 访问

把本仓库安装到兼容的 Agent Plugin 宿主，或在 Agent Skills 宿主中直接加载 `skills/infra-keeper/`。
**安装 Skill 或 Plugin 本身不会认证 GitHub，也不会安装其工具依赖。**

选择一种已获授权的后端：

- **GitHub MCP（优先）**：在 Agent 宿主中连接兼容的 GitHub MCP 服务器。官方实现：
  https://github.com/github/github-mcp-server
- **GitHub CLI（`gh`）**：适用于具备 shell 访问的本地 Agent，安装并认证
  https://cli.github.com/ ，随后用 `gh auth status` 验证。

两者可以同时配置，但**不需要都安装**：只要有一个后端可用即可正常工作。逐步骤的引导、最小权限
建议与故障排查见 [初始化向导](skills/infra-keeper/references/setup-wizard.md)。

安装与认证的环境细节见 [Hermes 桌面集成说明](docs/hermes.md)。

## 安全策略

- 常规文档变更直接提交到 `main`；不管理分支，不创建 PR。
- 读取、搜索、历史与状态检查可自动进行。
- **每一次写入**都必须事先就拟改路径、内容/diff、影响与回滚取得明确批准。
- 写入前检查并发修改；提交后重新读取提交记录与受影响文件。
- 不强制推送、不改写历史、不修改仓库管理设置，也不为绕过一次拒绝而切换到另一个后端。
- 仓库文档是**历史证据**，不是当前服务健康状态的证明。
- 绝不把凭据、私钥、令牌或敏感基础设施细节提交到公开示例中。
- 初始化向导自身只读：不创建测试提交，也不自动修改认证或宿主配置。

## 验证状态（2026-10-22）

Hermes 桌面已成功**加载插件与 Skill**，并通过 **GitHub CLI 与 GitHub MCP 两条路径**完成认证
读取、写入前审批与回读校验。两条后端还各自完成了一轮五阶段生命周期测试。

| 后端 | 证据 | 已验证 | 尚未测试 |
| --- | --- | --- | --- |
| GitHub CLI | [CLI 冒烟测试](tests/hermes-smoke-test.md)、[CLI 生命周期测试](tests/integration/cli-lifecycle.md) | 读取、审批、新建、按 Blob SHA 条件更新、并发编辑时停止、服务端拒绝过期 SHA（`409`）、按 Blob SHA 条件删除、逐字节恢复、回读 | 过期 `sha` 的**删除**是否被拒（只测了匹配值）、多文件原子提交、移动/重命名、权限拒绝行为、两个独立账号 |
| GitHub MCP | [MCP 冒烟测试](tests/hermes-mcp-smoke-test.md)、[MCP 生命周期测试](tests/integration/mcp-lifecycle.md) | 工具发现、读取、审批、新建、按 Blob SHA 条件更新、并发编辑时停止、删除、以新提交恢复、回读 | GitHub 侧版本强制（见下方说明）、多文件原子提交、移动/重命名、权限拒绝行为 |

**初始化向导状态**：向导协议已写入并提交，但尚未经过验收运行。上表报告的是各后端的 GitHub 访问
能力，不是向导本身的行为。

**关于冲突证据的范围说明**：过期版本写入是在 **MCP 写入路径**上被拒绝的，返回信息无法确定比较
发生在 MCP 服务器还是 GitHub API，因此本仓库**不**主张 GitHub 自身强制了版本检查。在 **CLI 后端**，
过期 SHA 的写入由 HTTP `409` 拒绝，响应携带 `Server: github.com` 与 GitHub 请求 ID，因此对 REST
Contents API 而言，本仓库主张 `sha` 前置条件由服务端强制。两类后端是彼此独立的证据，不可互换。

上述均为手工、单环境验收测试，**不是自动化一致性测试**。CLI 与 MCP 冒烟测试证据分别提交为
[CLI 测试 `09f4ad2`](https://github.com/NingAloha/infra-keeper/commit/09f4ad22076856123d2cc99674b36b32812a62cd)
与 [MCP 测试 `fb31c65`](https://github.com/NingAloha/infra-keeper/commit/fb31c65c3392c99a3e39007b39911f4b9fa3eb40)；
生命周期各阶段为提交
[`6f336ade`](https://github.com/NingAloha/infra-keeper/commit/6f336adeb15de0892b4fba2bf6a2367810f3ffd5)、
[`f87b3313`](https://github.com/NingAloha/infra-keeper/commit/f87b33138937139a96843efcef928c32bceae4c6)、
[`73fe73b8`](https://github.com/NingAloha/infra-keeper/commit/73fe73b8ce9329a19c4e5527e693fc8db36299ac)、
[`b95e8bee`](https://github.com/NingAloha/infra-keeper/commit/b95e8beebb738e6e33b9eb102b684ad1d07c1712)、
[`3be2869d`](https://github.com/NingAloha/infra-keeper/commit/3be2869d01527efb891213543003aec0c157e521)。
CLI 生命周期各阶段为提交
[`5d350208`](https://github.com/NingAloha/infra-keeper/commit/5d350208272823d861b42b93b6d79ad4b3cd538b)、
[`05a7c7f8`](https://github.com/NingAloha/infra-keeper/commit/05a7c7f8c7d84d82890b29f047f035a781808b0e)、
[`ed63fad4`](https://github.com/NingAloha/infra-keeper/commit/ed63fad49e650bccd1ef96d8c0ca2989924b2d6e)（网页编辑器）、
[`95b3d34b`](https://github.com/NingAloha/infra-keeper/commit/95b3d34b9ecde11fac08256c06b8504b5f3ba295)、
[`343b25fa`](https://github.com/NingAloha/infra-keeper/commit/343b25faf305dbc9514da12330c73965171156ce)；
C-2 的拒绝未产生提交。ChatGPT/Codex 插件安装尚未单独验证。

## 当前范围

只实现 **GitHub 支撑的文档工作流**。基础设施清单模板、实时 SSH/云操作、可复现的测试自动化、
完整多平台验证均为后续工作。**设备审计尚不存在**——初始化只负责准备该审计将要读取的仓库访问
权限。冲突处理已在两个后端上分别手工演练过，尚未自动化；在 MCP 后端，过期版本拒绝的强制层仍
未定位，在 CLI 后端已观察到发生在 GitHub API。本版本不提供 Local Workspace 或 Local Git 后端。
