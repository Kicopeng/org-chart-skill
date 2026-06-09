# Org Chart Generator

A one-click organizational chart generator for HR teams. A Claude Code skill.

## Features

- Extract organizational hierarchy from **natural language descriptions** or **Excel/CSV files**
- Automatically render tree-shaped org charts with rounded rectangle nodes and orthogonal connectors
- Support for **2-4 level** organizational structures with consistent 60px spacing between levels
- Three preset color schemes: **Tech Blue** (default) / **Business Gray** / **Forest Green**
- Auto-detect and display additional information: tenure, performance, title, etc.
- Output formats: **PPTX** (default) / **HTML** / **Markdown (Mermaid)**

## Installation

```bash
# Clone to Claude Code skills directory
git clone git@github.com:Kicopeng/org-chart-skill.git ~/.claude/skills/org-chart
```

After restarting your Claude Code session, type `/org-chart` or simply describe your organizational structure to trigger the skill.

## Usage Examples

### Method 1: Natural Language Description

```
Draw me an org chart.
NovaTech Inc., led by Sarah Chen (VP).
Departments: Business Analytics (James Huang), Merchandising (Michael Shen),
Warehousing (Leo Zhang), Product (Grace Guo), HR (David Sun), Finance (Alice Xuan)...
```

### Method 2: Excel File

```
Here's our personnel structure table, please generate an org chart.
[upload org_structure.xlsx]
```

### Method 3: JSON Data

```bash
# Generate HTML directly using the script
python scripts/generate.py data.json -o output.html --colors tech-blue
```

See `test_2level.json` and `test_3level.json` for data format examples.

## Project Structure

```
org-chart/
├── SKILL.md                        # Skill instructions (read by Claude)
├── README.md                       # This file
├── references/
│   ├── color-schemes.md            # Color palette reference
│   └── html-template.md            # HTML generation template and core logic
├── scripts/
│   ├── generate.py                 # HTML generation engine (Python)
│   └── screenshot.py               # Screenshot and PPTX embedding
└── test_*.json                     # Test cases
```

## Color Schemes

| Scheme | L1 (Root) | L2+ (Mid) | Leaf |
|--------|-----------|-----------|------|
| Tech Blue | `#1B2A31` dark blue | `#5399A0` light blue | `#ffffff` white |
| Business Gray | `#2D3436` dark gray | `#636E72` light gray | `#ffffff` white |
| Forest Green | `#1B4332` dark green | `#52B788` light green | `#ffffff` white |

## Connector Rules

All parent-child nodes are connected via orthogonal lines:
- Horizontal lines (vertical layout) precisely positioned at the midpoint between parent and child levels
- Child nodes evenly distributed with automatic spacing calculation
- Rendered using SVG paths for pixel-perfect precision

## Dependencies

- **Python 3.8+**
- **HTML generation**: No additional dependencies (standard library only)
- **PPTX output** requires:
  - `playwright` - for browser automation and screenshot capture
  - `python-pptx` - for PowerPoint file generation
  - `Pillow` - for image processing
  - The `/pptx` skill (optional, for alternative PPTX generation)

Install PPTX dependencies:
```bash
pip install playwright python-pptx Pillow
playwright install chromium
```

## License

MIT
