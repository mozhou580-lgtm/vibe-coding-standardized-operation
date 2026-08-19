# Vibe Coding 规范化操作 · 总安装

> 本文件是当前核心技能链的总安装入口。它只安装 PRD、Design、TDD 三个 Skill，不覆盖全局 `AGENTS.md` / `CLAUDE.md`，也不安装 Git Skill。

## 安装内容

```text
skills/
├── prd-master/SKILL.md
├── design-master/SKILL.md
└── tdd-master/SKILL.md
```

## 安装流程

1. 检查三个源目录及其 `SKILL.md` 是否存在、可读。
2. 按当前工具确定 Skill 根目录：
   - Claude Code：`~/.claude/skills/`
   - Codex：`~/.codex/skills/`
   - Windows 使用 `%USERPROFILE%\.claude\skills\` 或 `%USERPROFILE%\.codex\skills\`
3. 对每个目标 Skill 独立处理：
   - 目标不存在：直接复制完整目录。
   - 目标已存在：先备份到当前工具的 `backups/vibe-coding/skills/<skill-name>/<时间戳>`，再替换目标。
4. 备份必须位于 Skill 发现目录之外，避免旧版被识别为第二套 Skill。
5. 不删除或修改其他 Skill，不覆盖全局规则，不安装 `git-master`。
6. 安装后逐个验证：
   - `SKILL.md` 存在且可读。
   - YAML 的 `name` 与目录名一致。
   - `description` 非空。
   - 标题均以“Vibe Coding 规范化操作”开头。

## 可复制安装命令

在解压后的 `Vibe Coding 规范化操作/` 目录执行。脚本会先备份已有 Skill，再安装三个核心 Skill。

```bash
# Codex
bash ./install.sh codex

# Claude Code
bash ./install.sh claude

# 两个工具都安装
bash ./install.sh both
```

Windows PowerShell：

```powershell
.\install.ps1 -Target Codex
# 可选：Claude 或 Both
```

如果使用 Word Buddy 或 Cloud Agent，不写入本机目录：上传压缩包或 `skills/` 目录，并先让 Agent 读取本文件和三个 `SKILL.md`。

## 安装完成后的汇报

- 列出三个实际安装路径。
- 列出本次生成的备份路径；没有旧版则说明未产生备份。
- 提醒用户重启当前工具。
- 建议按顺序使用：

```text
开始 PRD → 接着做设计 → 生成 TDD 验收契约
```

## 失败处理

任一 Skill 安装失败时，说明具体失败点和已完成项；不要把部分成功报告成全部成功。源文件缺失、备份失败、写入无权限或安装后验证失败时，停止替换对应 Skill。
