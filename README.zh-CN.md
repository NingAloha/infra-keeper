# InfraKeeper

[English](README.md) | **简体中文**

InfraKeeper 是一个实验性的 **Agent Plugin**，封装了一份标准 **Agent Skill**，用于基于证据维护基础设施文档。

## 快速开始

1. 在兼容的 Agent Plugin 宿主中安装本仓库（见下文）。
2. 输入 **「初始化 InfraKeeper」** 或 **「Set up InfraKeeper」**。Skill 会启动初始化向导；首次没有绑定
   仓库时会引导创建一次个人仓库，之后只做校验。
3. 向导会先在 Agent 页面检测本机 **GitHub CLI（`gh`）**。如果没有安装，它会根据你的系统
   展示官方安装命令和影响；你批准后，优先由 Agent 页面执行，完成后自动重新检测。
4. 如果尚未登录，向导会在 Agent 页面展示 `gh auth login` 并请求单独批准；你在浏览器中完成
   授权即可。如果宿主不支持交互终端，才退回让你在本机终端执行。它不会接收、显示或保存 Token。
5. 首次配置时给仓库起一个名字，默认是 `infrastructure`。如果该名字已存在，向导会要求换一个未
   使用的名字；创建个人私有仓库前会单独请求一次批准。之后启动只验证已绑定的仓库。CLI 判定为：
   `ready`、`unavailable`、`unauthenticated`、`insufficient-permissions`、`out-of-scope` 或 `unverified`。

本版本只允许操作**当前登录 GitHub 用户自己拥有的仓库**。组织仓库、协作者仓库和其他用户的公开
仓库，即使当前账号有访问权限，也会被拒绝。

向导在首次创建完成后对 GitHub 仓库是**只读的**。首次只允许创建一次你本人名下的私有仓库和
初始 README；创建前必须展示完整计划并获得单独批准。它不会创建测试提交或测试文件，也不会静默
安装软件、修改宿主配置、环境变量或凭据文件。Token 和浏览器授权始终由你本人处理。

S5 成功后，InfraKeeper 会在本机应用状态文件中只保存绑定元数据：仓库、`main` 分支、首次创建
状态和可选的初始提交 SHA。它不会保存 Token、`gh` 凭据或仓库内容。每次新会话先读取该文件，再
重新校验记录的仓库后再使用；如果文件不存在或无效，就重新询问仓库名称。

初始化结束时会指向设备审计。该审计在**本版本中尚未实现**。

## 包结构

```text
README.md
README.zh-CN.md
plugin.json
skills/infra-keeper/scripts/gh_backend.py
skills/infra-keeper/SKILL.md
skills/infra-keeper/references/
  github-backends.md
  github-cli.md
  github-workflow.md
  setup-wizard.md
docs/hermes.md
tests/
  test_gh_backend.py
  hermes-smoke-test.md
  integration/cli-lifecycle.md
```

插件打包面向 [Agent Plugins](https://agent-plugins.org/specification)；内嵌 Skill 遵循
[Agent Skills 规范](https://agentskills.io/specification)。各宿主的兼容性需分别验证。

## 安装与 GitHub 访问

把本仓库安装到兼容的 Agent Plugin 宿主，或在 Agent Skills 宿主中直接加载 `skills/infra-keeper/`。
**安装 Skill 或 Plugin 本身不会静默认证 GitHub 或修改本机配置。** 初始化向导会检测 `gh`；如果
缺失，会给出 macOS、Windows 或 Linux 的官方安装路径。默认会在 Agent 页面确认后执行具体命令；
只有 Agent 宿主不支持命令执行或交互终端时，才让你在本机执行。认证同样需要单独批准，浏览器授权
由你本人完成。

选择一种已获授权的后端：

- **GitHub CLI（`gh`）**：适用于具备 shell 访问的本地 Agent，安装并认证
  https://cli.github.com/ ，随后用 `gh auth status` 验证。

插件内的 `skills/infra-keeper/scripts/gh_backend.py` 会把常用 GitHub 操作包装成结构化 JSON，
并对写入强制要求审批和 SHA 前置条件。逐步骤的引导、最小权限建议与故障排查见
[初始化向导](skills/infra-keeper/references/setup-wizard.md)。

安装与认证的环境细节见 [Hermes 桌面集成说明](docs/hermes.md)。

## 安全策略

- 常规文档变更直接提交到 `main`；不管理分支，不创建 PR。
- 目标仓库 owner 必须与 `gh` 当前登录用户一致；不操作组织、协作者或其他用户的仓库。
- 首次无绑定时可创建一次个人私有仓库；后续初始化只校验绑定，不重复创建或申请仓库权限。
- 读取、搜索、历史与状态检查可自动进行。
- **每一次写入**都必须事先就拟改路径、内容/diff、影响与回滚取得明确批准。
- 写入前检查并发修改；提交后重新读取提交记录与受影响文件。
- 不强制推送、不改写历史、不修改仓库管理设置，也不为绕过一次拒绝而切换到另一个后端。
- 仓库文档是**历史证据**，不是当前服务健康状态的证明。
- 绝不把凭据、私钥、令牌或敏感基础设施细节提交到公开示例中。
- 初始化向导除首次单独批准的仓库创建外不写 GitHub 内容，也不创建测试提交；本机安装或登录只有在单独批准具体命令后才会执行。

## 验证状态（2026-10-22）

Hermes 桌面已成功**加载插件与 Skill**，并通过 **GitHub CLI** 完成认证读取、写入前审批与回读
校验。CLI 路径还完成了一轮五阶段生命周期测试。

| 后端 | 证据 | 已验证 | 尚未测试 |
| --- | --- | --- | --- |
| GitHub CLI | [CLI 冒烟测试](tests/hermes-smoke-test.md)、[CLI 生命周期测试](tests/integration/cli-lifecycle.md) | 读取、审批、新建、按 Blob SHA 条件更新、并发编辑时停止、服务端拒绝过期 SHA（`409`）、按 Blob SHA 条件删除、逐字节恢复、回读 | 过期 `sha` 的**删除**是否被拒（只测了匹配值）、多文件原子提交、移动/重命名、权限拒绝行为、两个独立账号 |
| 内置 CLI 辅助脚本 | [单元测试](tests/test_gh_backend.py) | JSON CLI 参数校验、审批门、过期 Blob SHA 拒绝 | 真实 GitHub 端到端运行、跨宿主安装 |

**初始化向导状态**：向导协议已写入并提交，但尚未经过验收运行。上表报告的是 CLI 和辅助脚本的
验证状态，不是向导本身的行为。

**关于冲突证据的范围说明**：当前唯一后端是 GitHub CLI。过期 SHA 的写入由 HTTP `409` 拒绝，
响应携带 `Server: github.com` 与 GitHub 请求 ID，因此对 REST Contents API 而言，本仓库主张
`sha` 前置条件由服务端强制。

上述均为手工、单环境验收测试，**不是自动化一致性测试**。CLI 冒烟测试证据提交为
[CLI 测试 `09f4ad2`](https://github.com/NingAloha/infra-keeper/commit/09f4ad22076856123d2cc99674b36b32812a62cd)；
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
权限。冲突处理已通过 GitHub CLI 手工演练，并由插件内 CLI 辅助脚本的单元测试覆盖审批门和版本
冲突检查。本版本不提供 GitHub MCP、Local Workspace 或 Local Git 后端。
