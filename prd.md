# Vibe Coding 规范化操作 · PRD Master 安装

> 本文件只负责安装 `prd-master`。实际工作流程全部位于 `skills/prd-master/SKILL.md`。

## 安装要求

1. 使用当前安装包中的 `skills/prd-master/`，不从未知地址下载替代内容。
2. 解包或复制前确认 `skills/prd-master/SKILL.md` 存在且可读。
3. 按当前工具选择安装位置：
   - Claude Code：`~/.claude/skills/prd-master`
   - Codex：`~/.codex/skills/prd-master`
   - Windows 使用 `%USERPROFILE%\.claude\skills\prd-master` 或 `%USERPROFILE%\.codex\skills\prd-master`
4. 目标目录已存在时，先完整备份到 Skill 发现目录之外：
   - Claude Code：`~/.claude/backups/vibe-coding/skills/prd-master/<时间戳>`
   - Codex：`~/.codex/backups/vibe-coding/skills/prd-master/<时间戳>`
5. 备份成功后再替换 `prd-master` 目录，不影响其他 Skill。
6. 安装后检查：
   - `SKILL.md` 第一段 YAML 包含 `name: prd-master` 和非空 `description`。
   - 文件标题为“Vibe Coding 规范化操作 · PRD Master”。
   - `templates/requirements.md` 和 `validators/check_requirements_contract.py` 存在且可读；校验器只依赖 Python 标准库。
   - 文件可读且没有被截断。

## 可复制命令

从安装包根目录执行：

```bash
bash ./install.sh codex
```

只手动安装本 Skill 时，目标目录为 `~/.codex/skills/prd-master`；Claude Code 使用 `~/.claude/skills/prd-master`。安装完成后重启工具，再说“开始 PRD”。

## 安装完成后的汇报

- 告知实际安装路径。
- 若产生备份，告知备份路径。
- 提醒用户重启当前工具。
- 重启后可以说：“开始 PRD”“梳理这个产品想法”或“继续上次的 PRD”。

## 失败处理

任何复制、备份或验证失败都要如实说明。没有通过安装后检查时，不得声称安装成功，也不得用临时摘要替代 `SKILL.md`。
