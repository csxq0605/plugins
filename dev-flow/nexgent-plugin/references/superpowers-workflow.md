# Superpowers Workflow — dev-flow 集成

dev-flow 在 superpowers 工作流的每个阶段都有对应能力：

## Step 0: 项目文档布局
- `devflow_onboard` — 扫描项目结构和技术栈

## Step 1: Brainstorming
- `devflow_memory_recall` — 回忆之前的决策和发现
- `devflow_adr_create` — 记录设计决策

## Step 2: Writing-plans
- `devflow_audit` — 检查依赖安全

## Step 8: Review
- `devflow_review_start/add/score/export` — 6 视角代码审查

## Step 10: Merge + Cleanup
- `devflow_changelog` — 生成变更日志
- `devflow_memory_save` — 保存会话记忆
- `devflow_adr_list` — 确认决策状态

## 与 team-coord 集成

Lead 可分配 worker 并行执行：
- Worker A → onboard + audit
- Worker B → review
- Worker C → changelog + memory
