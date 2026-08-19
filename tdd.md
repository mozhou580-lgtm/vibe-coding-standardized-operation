# Vibe Coding 规范化操作 · TDD Master 安装

> 本文件只负责安装 `tdd-master`。实际工作流程全部位于 `skills/tdd-master/SKILL.md`。

## 安装要求

1. 使用当前安装包中的 `skills/tdd-master/`。
2. 安装前确认 `skills/tdd-master/SKILL.md` 存在且可读。
3. 按当前工具选择安装位置：
   - Claude Code：`~/.claude/skills/tdd-master`
   - Codex：`~/.codex/skills/tdd-master`
   - Windows 使用 `%USERPROFILE%\.claude\skills\tdd-master` 或 `%USERPROFILE%\.codex\skills\tdd-master`
4. 目标目录已存在时，先完整备份到 Skill 发现目录之外：
   - Claude Code：`~/.claude/backups/vibe-coding/skills/tdd-master/<时间戳>`
   - Codex：`~/.codex/backups/vibe-coding/skills/tdd-master/<时间戳>`
5. 备份成功后再替换 `tdd-master` 目录，不影响其他 Skill。
6. 安装后检查：
   - YAML 包含 `name: tdd-master` 和非空 `description`。
   - 标题为“Vibe Coding 规范化操作 · TDD Master”。
   - `validators/check_delivery_contract.py` 存在且可读；它只依赖 Python 标准库。
   - 文件可读且没有被截断。

## 可复制命令

推荐从安装包根目录一次安装三个核心 Skill：

```bash
bash ./install.sh codex
```

只手动安装本 Skill 时，目标目录为 `~/.codex/skills/tdd-master`；Claude Code 使用 `~/.claude/skills/tdd-master`。安装完成后重启工具，再说“生成 TDD 验收契约”。

## 安装完成后的汇报

- 告知安装路径和备份路径。
- 提醒用户重启当前工具。
- Design 完成后可以说：“生成 TDD 验收契约”“定义怎么算完成”或“继续做 TDD”。

## 失败处理

验证未通过时停止并如实说明。不得跳过上游 PRD/Design 契约，不得用普通任务清单冒充 `TDD验收契约.md`。
