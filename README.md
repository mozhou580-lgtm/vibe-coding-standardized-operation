# Vibe Coding 规范化操作

## 这是什么

这是一套面向非技术业务人员的 AI 产品协作规范。当前核心保留 PRD、Design 和 TDD 的工程能力，并把它们翻译成业务人员能够参与的流程；Git 协作暂作为后续可选扩展。

本目录可直接打包为 `Vibe Coding 规范化操作_完整安装包.zip` 分发；不要只复制某一个 `SKILL.md`，否则模板、校验器和安装脚本会缺失。

GitHub 公共安装仓库：<https://github.com/mozhou580-lgtm/vibe-coding-standardized-operation>

## 适用人群

- 任何需要把业务想法交给 AI 或开发人员落地的人。
- 跨境电商、国内电商和 B 端销售是优先验证的示例场景，不是使用范围限制。
- 其他部门可直接从具体工作任务进入，不需要先匹配行业模板。

## 核心改变

1. 先问“你想做出什么、谁会怎么用”，再补充价值，不把宏观价值论证设成启动门槛。
2. AI 先给出可视化的产品草图和推荐方案；没有重大分叉时默认继续，不反复追问。
3. 只对会改变产品边界、数据责任、合规风险或返工成本的事项提问。
4. Design 按风险输出施工图，TDD 输出可执行验收契约；Git 暂不进入个人创作核心链路。
5. 先用业务场景验证，再决定是否需要完整工程化产物。

## 使用顺序

```text
业务想法
  ↓
PRD：把“我想要的东西”说成可执行的产品草图
  ↓
Design：把草图翻译成页面、流程、状态和实现建议
  ↓
TDD：把“怎么算做完”翻译成可执行验收契约
  ↓
Vibe Coding：按最小闭环开发、演示、修正
```

## 最快安装

安装包解压后，进入 `Vibe Coding 规范化操作/` 目录。脚本只安装 `prd-master`、`design-master`、`tdd-master`，会先把已有版本移动到备份目录，不覆盖全局规则。

最短在线安装（Codex）：

```bash
curl -fsSL https://raw.githubusercontent.com/mozhou580-lgtm/vibe-coding-standardized-operation/main/install-online.sh | bash -s -- codex
```

### macOS / Linux：Codex

```bash
unzip "Vibe Coding 规范化操作_完整安装包.zip" -d /tmp/vibe-coding-install
cd "/tmp/vibe-coding-install/Vibe Coding 规范化操作"
bash ./install.sh codex
```

### macOS / Linux：Claude Code

```bash
bash ./install.sh claude
```

同时安装到两个工具：

```bash
bash ./install.sh both
```

### Windows PowerShell

```powershell
Expand-Archive .\Vibe Coding 规范化操作_完整安装包.zip -DestinationPath $env:TEMP\vibe-coding-install
Set-Location "$env:TEMP\vibe-coding-install\Vibe Coding 规范化操作"
.\install.ps1 -Target Codex
```

将 `Codex` 改为 `Claude`，或使用 `Both` 同时安装。安装完成后重启工具。

### Word Buddy / Cloud Agent

这类工具通常不需要写入本机 Skill 目录。直接上传 `Vibe Coding 规范化操作_完整安装包.zip` 或解压后的 `skills/` 目录，并发送：

```text
请先读取 claude.md，再按 PRD → Design → TDD 使用三个 SKILL.md；不要把 Git 作为当前主流程。
```

### 安装后的第一句话

```text
开始 PRD：这是我想做的工作……请先回放理解，给一版 MVP 推荐，只问会改变结果的问题。
```

## 文件导航

- [工作流总览.md](./工作流总览.md)：总规则、模式和翻译表。
- [prd.md](./prd.md)：PRD Master 单项安装说明。
- [design.md](./design.md)：Design Master 单项安装说明。
- [tdd.md](./tdd.md)：TDD Master 单项安装说明。
- [GIT.md](./GIT.md)：可选扩展，当前个人创作链路暂不启用。
- [业务场景模板.md](./业务场景模板.md)：跨境电商、国内电商、B 端销售模板。
- [迁移说明.md](./迁移说明.md)：与原始资料的对应关系和删减项。
- `install.sh` / `install.ps1`：macOS/Linux 和 Windows 的可逆安装脚本。

## 运行边界

- 默认使用“快速模式”；只有风险高、需求冲突或需要多人交接时才升级为“标准模式”。
- AI 推荐项默认采用，用户只需指出不同意见；不把“确认推荐”重复问成多轮。
- 不自动安装、不自动覆盖全局配置、不自动提交或推送代码。
- 任何涉及删除、生产配置、凭据、权限和远端仓库的动作，都必须获得当次明确授权。
