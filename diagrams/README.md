# Mermaid Diagrams

Source `.mmd` files cho toàn bộ kiến trúc. Có thể render ra PNG bằng Mermaid CLI.

## Danh sách

| File | Mô tả |
|------|-------|
| `01_architecture_overview.mmd` | Sơ đồ tổng quan kiến trúc Router-Centric ReAct |
| `02_router_logic.mmd` | Flowchart logic routing decision |
| `03_react_loop.mmd` | State diagram cho ReAct loop |
| `04_proactive_event.mmd` | Sequence diagram cho background event flow |
| `05_deployment.mmd` | Sơ đồ triển khai (deployment) |
| `06_database_erd.mmd` | Entity Relationship Diagram cho database |

## Render PNG

Sử dụng Mermaid CLI (đã cài trong `node_modules` của dự án cha):

```bash
npx -p @mermaid-js/mermaid-cli mmdc -i diagrams/01_architecture_overview.mmd -o diagrams/01_architecture_overview.png
```

Hoặc batch:
```bash
for f in diagrams/*.mmd; do
    npx -p @mermaid-js/mermaid-cli mmdc -i "$f" -o "${f%.mmd}.png"
done
```

## Xem Online

Có thể paste nội dung `.mmd` vào:
- https://mermaid.live
- GitHub Markdown (render tự động trong `.md` files)

## Diagrams trong Design Docs

Một số diagrams đã được nhúng trong các file `.md` ở `docs/`:

| Doc | Diagrams |
|-----|----------|
| `01_architecture_overview.md` | Main architecture diagram |
| `02_router_gateway_design.md` | Entry point flow |
| `03_system1_fast_layer.md` | Pipeline |
| `04_system2_react_agent.md` | ReAct loop state |
| `05_user_modeling_layer.md` | 4 components |
| `06_dynamic_tool_registry.md` | 3 toolkits |
| `07_proactive_reminders.md` | Cron + Event flow |
| `08_data_flow_and_diagrams.md` | ERD, sequence, deployment |

## Style

Tất cả diagrams sử dụng classDef để có màu sắc nhất quán:
- 🔵 Blue: User/Input
- 🔴 Red: Router/Critical
- 🟢 Green: System 2 / API
- 🟡 Yellow: Decisions
- 🟠 Orange: Database
- 🟣 Purple: Workers / LLM
- ⚫ Gray: External services
