# 文档导航（唯一官方入口）

> 维护原则：以代码为准（SSOT）。本目录为唯一官方文档入口；`docs/_archive/` 仅存档不维护。

## 建议阅读顺序（毕业设计/答辩）
1. `00-overview/project-overview.md`
2. `10-product/core-flows.md`
3. `20-architecture/system-architecture.md`
4. `20-architecture/database-design.md`
5. `30-api/api-guide.md` + `30-api/api-reference.generated.md`
6. `70-ui/ui-guidelines.md`
7. `50-testing/test-plan.md`
8. `40-dev-guide/runbook.md`
9. `maintenance/change-workflow.md` + `changelog.md`

## 文档更新规则（必须遵守）
1. 每次功能变更必须同时提交：
   - 变更单：`docs/maintenance/changes/YYYY-MM-DD-change-xxx.md`
   - 文档更新：仅更新变更单列出的文件
   - Changelog：`docs/changelog.md` 一行一条
2. 不确定处标记 `TODO: needs confirmation`，禁止编造。
3. “事实型内容”的权威来源（SSOT）：
   - 接口与行为：后端路由/视图与前端调用
   - 数据结构：`models.py` 与 migrations
   - 配置：`.env.example`、启动脚本、部署配置
4. 同一事实只允许在一个地方定义（例如状态机只写在 `core-flows.md`）。

## 自动生成（推荐）
- API 参考生成：`python scripts/generate_api_reference.py`
-（可选）提交前脚本：`bash scripts/update_docs.sh`
