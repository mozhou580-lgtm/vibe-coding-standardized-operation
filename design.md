# Vibe Coding 规范化操作 · Design Master 安装

> 本文件只负责安装 `design-master`。实际工作流程全部位于 `skills/design-master/SKILL.md`。

## 安装要求

1. 使用当前安装包中的 `skills/design-master/`。
2. 安装前确认 `skills/design-master/SKILL.md` 存在且可读。
3. 按当前工具选择安装位置：
   - Claude Code：`~/.claude/skills/design-master`
   - Codex：`~/.codex/skills/design-master`
   - Windows 使用 `%USERPROFILE%\.claude\skills\design-master` 或 `%USERPROFILE%\.codex\skills\design-master`
4. 目标目录已存在时，先完整备份到 Skill 发现目录之外：
   - Claude Code：`~/.claude/backups/vibe-coding/skills/design-master/<时间戳>`
   - Codex：`~/.codex/backups/vibe-coding/skills/design-master/<时间戳>`
5. 备份成功后再替换 `design-master` 目录，不影响其他 Skill。
6. 安装后检查：
   - YAML 包含 `name: design-master` 和非空 `description`。
   - 标题为“Vibe Coding 规范化操作 · Design Master”。
   - `templates/page.md`、`templates/technical-plan.md`、`templates/page-html.md` 和 `validators/check_traceability.py`、`validators/check_html_contract.py` 存在且可读；校验器只依赖 Python 标准库。
   - 文件可读且没有被截断。

## 可复制命令

推荐从安装包根目录一次安装三个核心 Skill：

```bash
bash ./install.sh codex
```

只手动安装本 Skill 时，目标目录为 `~/.codex/skills/design-master`；Claude Code 使用 `~/.claude/skills/design-master`。安装完成后重启工具，再说“接着做设计”。

## 安装完成后的汇报

- 告知安装路径和备份路径。
- 提醒用户重启当前工具。
- PRD 已完成后可以说：“接着做设计”“把 PRD 变成施工图”或“生成标准 Design 交付”。

## 失败处理

验证未通过时停止并说明失败点。不得覆盖其他 Skill，不得把旧备份放进 Skill 发现目录，也不得声称未完成的安装已成功。
