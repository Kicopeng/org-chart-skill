# Color Schemes

## Palette System

Each scheme defines a palette array — one entry per hierarchy level, top to bottom.

**Leaf nodes are always `#FFFFFF` (white)** with text color inherited from the deepest palette entry.

### 1. Tech Blue (default)

| Level | Background | Text | Role |
|-------|-----------|------|------|
| L1 | `#1B2A31` | `#FFFFFF` | Root / CEO |
| L2 | `#5399A0` | `#FFFFFF` | Division heads |
| L3 | `#98C3C7` | `#1B2A31` | Team leads |
| L4 | `#BE9F89` | `#1B2A31` | Sub-team leads |
| Leaf | `#FFFFFF` | *auto* | Members |

### 2. Business Gray

| Level | Background | Text |
|-------|-----------|------|
| L1 | `#2D3436` | `#FFFFFF` |
| L2 | `#636E72` | `#FFFFFF` |
| L3 | `#B2BEC3` | `#2D3436` |
| Leaf | `#FFFFFF` | *auto* |

### 3. Forest Green

| Level | Background | Text |
|-------|-----------|------|
| L1 | `#1B4332` | `#FFFFFF` |
| L2 | `#52B788` | `#FFFFFF` |
| L3 | `#95D5B2` | `#1B4332` |
| Leaf | `#FFFFFF` | *auto* |

## Rules

- Beyond the defined palette, mid-levels reuse the last palette entry
- Leaf nodes are always white regardless of depth
- Text color on white leaves is auto-picked from the deepest palette entry
