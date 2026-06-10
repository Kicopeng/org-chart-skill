---
name: org-chart
description: "Assist drawing organizational charts. When user wants to use natural language or Excel/CSV to record organization structure, with this skill, org chart can be generated. Trigger words: org chart, organization chart, department chart, reporting line. Default output: PPTX, HTML and Mermaid Markdown."
---

# Org Chart Generator

One-click org chart generator for HR teams.

## Process

### Phase 1: Collect Data

Two input methods:

**A. Natural Language** — parse hierarchy from user description:
- Department name (required)
- Leader (optional)
- Responsibilities (optional)
- Extra fields: tenure, performance rating, title, employee ID, location, etc. (optional, auto-detected)

**B. Excel/CSV File** — if a file is provided, use `/xlsx` skill to read and auto-map columns to fields.

### Phase 2: Confirm Three Settings

Ask sequentially, recommend one each time:

| Setting | Default | Notes |
|---------|---------|-------|
| Layout | Vertical | 2-4 levels recommended; vertical layout only |
| Colors | Tech Blue | See `references/color-schemes.md` |
| Output | PPTX | Also supports HTML and Markdown (Mermaid) |

### Phase 3: Draw

#### Node Rules

- All nodes use **rounded rectangles** (radius: 12-16px)
- Node content order: `name` (bold) -> `leader` (red/gray) -> `responsibilities` (small gray) -> `extra tags` (tenure, performance, etc.)
- Leader: filled = `#e06070` red, vacant = `#bbb` gray + italic

#### Color Rules

- Defined as a palette array: one entry per hierarchy level, top to bottom
- **Leaf nodes are always `#FFFFFF` (white)**
- See `references/color-schemes.md` for full palettes

#### Connector Lines

```
      [Parent]
         |
    =========
     |   |   |
  [C1] [C2] [C3]
```
- Level gap: 60px (adjustable +-10px)
- All horizontal lines at exact midpoint of the parent-child gap

#### Implementation

Use **SVG `<path>`** for connector lines:
1. Overlay `<svg>` layer: `position:absolute; z-index:0; pointer-events:none`
2. Measure node positions via `getBoundingClientRect()`
3. H-line Y = `(parentBottom + childTop) / 2` (exact midpoint)
4. Build path: horizontal span + vertical drops + root vertical

See `references/html-template.md` for validated template code.

### Phase 4: Output

- **HTML**: `python scripts/generate.py data.json -f html`
- **PPTX** (default): generate HTML with white bg -> screenshot via Playwright -> embed in PPTX
- **Mermaid Markdown**: `python scripts/generate.py data.json -f mermaid`

## Example

```
User: Here's our org structure spreadsheet, generate an org chart
      [uploads org_structure.xlsx]

Assistant:
  Read the file. Detected 3-level structure:
  - CEO (1)
  - Departments (5)
  - Sub-teams (14)

  Three quick confirmations:
  1. Color scheme: Tech Blue?
  2. Output format: PPTX (default)?

User: Tech Blue, PPTX

Assistant:
  [Generates PPTX]
  Saved: Org_Chart.pptx
  3 levels, 20 nodes, vertical layout, Tech Blue palette
```

## References

- Color schemes: `references/color-schemes.md`
- HTML template & line-drawing logic: `references/html-template.md`
- All paths relative to `~/.claude/skills/org-chart/`

---

# 组织架构图生成器

面向 HR 的一键组织架构图生成工具。

## 处理流程

### Phase 1：收集信息

两种输入方式：

**A. 自然语言** — 用户直接描述层级结构。逐层解析：
- 部门名称（必填）
- 负责人（选填）
- 职责描述（选填）
- 附加字段：司龄、绩效、职务、工号、base地等（可选，自动检测并展示）

**B. Excel/CSV 文件** — 如果用户提供了文件，调用 `/xlsx` skill 读取，自动映射列名到字段。

### Phase 2：与用户确认三项设置

依次询问，每项给推荐值并说明理由：

| 设置 | 推荐值 | 说明 |
|------|--------|------|
| 布局 | 竖版 | 2-4层推荐竖版 |
| 配色 | 科技蓝 | 见 `references/color-schemes.md`，也可选商务灰或墨绿 |
| 输出 | PPTX | 默认 PPTX，方便汇报演示；也可 HTML 或 MD |

### Phase 3：绘制架构图

#### 节点规则

- 所有节点为**圆角矩形**（radius: 12-16px）
- 节点内容层级：`部门名称`（加粗）→ `负责人`（红色/灰色）→ `职责描述`（小字灰）→ `附加标签`（司龄/绩效等用小 tag）
- 负责人：有值为 #e06070 红色，空缺/待任命为 #bbb 灰色+斜体

#### 配色规则

- 按层级数组定义，从高到低
- **最末节点一定为白色（#FFFFFF）**
- 完整配色表见 `references/color-schemes.md`

#### 连线规则

```
      [父节点]
         │
    =========
     │   │   │
  [子1] [子2] [子3]
```
- 层级间距：60px（可微调 ±10px）
- 所有横线在同一水平线，位于父子层级间隙的正中间

#### 连线实现

使用 **SVG `<path>`** 绘制折线：
1. 在容器上叠加 `<svg>` 层（`position:absolute; z-index:0; pointer-events:none`）
2. 用 `getBoundingClientRect()` 测量每个节点的实际坐标
3. 横线 Y = `(parentBottom + childTop) / 2`（精确中位）
4. 构建 path: 横线 + 子节点竖线 + 根节点竖线

参考 `references/html-template.md` 获取经过验证的完整模板代码。

### Phase 4：输出

- **HTML**：`python scripts/generate.py data.json -f html`
- **PPTX**（默认）：生成白底 HTML → Playwright 截图 → 嵌入 PPTX
- **Mermaid Markdown**：`python scripts/generate.py data.json -f mermaid`

## 示例对话

```
User: 这是我们的组织架构表，帮我画个架构图
      [上传 org_structure.xlsx]

Assistant:
  已读取表格，识别到 3 层结构：
  - CEO（1人）
  - 一级部门（5个）
  - 二级部门（14个）
  
  确认两件事：
  ① 配色用科技蓝？
  ② 输出 PPTX？

User: 科技蓝，PPTX

Assistant:
  [生成 PPTX 文件]
  已生成 Org_Chart.pptx
  3 层结构，20 个节点，科技蓝配色
```

## 参考文件

- 配色完整定义：`references/color-schemes.md`
- HTML 生成模板：`references/html-template.md`
- 所有路径相对于 `~/.claude/skills/org-chart/`
