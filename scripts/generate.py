#!/usr/bin/env python3
"""Org chart HTML generator.

Takes a JSON file describing an organizational hierarchy and produces a
standalone HTML file with CSS styling and SVG connector lines.

Usage:
    python generate.py data.json -o output.html
    python generate.py data.json -o output.html --colors business
"""

import json
import html as html_mod
import argparse
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
import screenshot


VACANT_MARKERS = ("-", "Vacant", "TBD", "")

COLOR_SCHEMES = {
    "tech-blue": {
        "palette": [
            {"bg": "#1B2A31", "fg": "#ffffff"},
            {"bg": "#5399A0", "fg": "#ffffff"},
            {"bg": "#98C3C7", "fg": "#1B2A31"},
            {"bg": "#BE9F89", "fg": "#1B2A31"},
        ],
        "leader_filled": "#e06070",
        "leader_empty": "#bbbbbb",
        "desc_color": "#999999",
        "tag_bg": "#f4f5f9",
        "tag_color": "#888888",
        "line_color": "#c0c4cc",
        "card_shadow": "0 2px 14px rgba(0,0,0,.05)",
        "card_border": "#eeeeee",
        "bg": "#f7f8fa",
    },
    "business-gray": {
        "palette": [
            {"bg": "#2d3436", "fg": "#ffffff"},
            {"bg": "#636e72", "fg": "#ffffff"},
            {"bg": "#b2bec3", "fg": "#2d3436"},
        ],
        "leader_filled": "#d63031",
        "leader_empty": "#bbbbbb",
        "desc_color": "#999999",
        "tag_bg": "#f5f5f5",
        "tag_color": "#777777",
        "line_color": "#b2bec3",
        "card_shadow": "0 2px 14px rgba(0,0,0,.06)",
        "card_border": "#dfe6e9",
        "bg": "#f5f6fa",
    },
    "forest-green": {
        "palette": [
            {"bg": "#1b4332", "fg": "#ffffff"},
            {"bg": "#52b788", "fg": "#ffffff"},
            {"bg": "#95d5b2", "fg": "#1b4332"},
        ],
        "leader_filled": "#e06070",
        "leader_empty": "#bbbbbb",
        "desc_color": "#999999",
        "tag_bg": "#f0faf5",
        "tag_color": "#666666",
        "line_color": "#95d5b2",
        "card_shadow": "0 2px 14px rgba(0,0,0,.05)",
        "card_border": "#d8f3dc",
        "bg": "#f7faf8",
    },
}


def validate_tree(node: dict[str, Any], path: str = "root") -> None:
    """Validate org tree structure, raising ValueError on invalid data."""
    if not isinstance(node, dict):
        raise ValueError(f"{path}: expected object, got {type(node).__name__}")
    if "name" not in node or not isinstance(node["name"], str):
        raise ValueError(f"{path}: 'name' field is required and must be a string")
    children = node.get("children")
    if children is not None:
        if not isinstance(children, list):
            raise ValueError(f"{path}.children: must be an array")
        for i, child in enumerate(children):
            validate_tree(child, f"{path}.children[{i}]")


def load_json(path: str) -> dict[str, Any]:
    """Load and validate a JSON org tree file."""
    with open(path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    validate_tree(data)
    return data


def get_tree_depth(node: dict[str, Any]) -> int:
    """Return the maximum depth of the tree."""
    children = node.get("children")
    if not children:
        return 1
    return 1 + max(get_tree_depth(c) for c in children)


def _resolve_card_style(level: int, is_leaf: bool, colors: dict[str, Any]) -> tuple[str, str]:
    """Resolve background, foreground, and CSS modifiers for a node card."""
    palette = colors["palette"]
    idx = min(level, len(palette) - 1)
    if is_leaf:
        bg, fg = "#ffffff", palette[idx]["bg"]
        return f"background:{bg};color:{fg};border-radius:12px;padding:16px 14px;", "leaf"
    bg, fg = palette[idx]["bg"], palette[idx]["fg"]
    if level == 0:
        return f"background:{bg};color:{fg};border-radius:16px;padding:22px 56px;", "root"
    return f"background:{bg};color:{fg};border-radius:14px;padding:18px 20px;", "mid"


def node_card_html(node: dict[str, Any], level: int, colors: dict[str, Any]) -> str:
    """Render a single node card as HTML."""
    name = html_mod.escape(node.get("name", ""))
    leader = html_mod.escape(node.get("leader", "") or "")
    resp_list = [html_mod.escape(r) for r in node.get("responsibilities", [])]
    resp = " · ".join(resp_list) if resp_list else ""
    meta = {html_mod.escape(k): html_mod.escape(v) for k, v in node.get("meta", {}).items()}

    is_leaf = not node.get("children")
    style, card_class = _resolve_card_style(level, is_leaf, colors)

    shadow = colors["card_shadow"]
    if level == 0:
        shadow = "0 8px 32px rgba(26,26,46,.18)"
    border_css = f"border:1px solid {colors['card_border']};" if is_leaf else ""
    full_style = f"{style};text-align:center;box-shadow:{shadow};{border_css}"

    if leader and leader not in VACANT_MARKERS:
        leader_html = (
            f'<div class="nl-filled" style="color:{colors["leader_filled"]};">'
            f'{leader}</div>'
        )
    else:
        display = leader if leader and leader != "-" else "TBD"
        leader_html = (
            f'<div class="nl-empty" style="color:{colors["leader_empty"]};">'
            f'{display}</div>'
        )

    resp_html = ""
    if resp:
        resp_html = (
            f'<div class="nr" style="color:{colors["desc_color"]};">'
            f'{resp}</div>'
        )

    tags_html = ""
    if meta:
        tag_items = " ".join(
            f'<span class="nt" style="color:{colors["tag_color"]};background:{colors["tag_bg"]};">'
            f'{k} {v}</span>'
            for k, v in meta.items()
        )
        tags_html = f'<div class="nt-wrap">{tag_items}</div>'

    return (
        f'<div class="nc {card_class}" style="{full_style}">'
        f'<div class="nn">{name}</div>'
        f'{leader_html}{resp_html}{tags_html}'
        f'</div>'
    )


def render_subtree(node: dict[str, Any], level: int, colors: dict[str, Any]) -> str:
    """Recursively render a subtree: node card + children as a grouped row."""
    parts = []
    parts.append(f'<div class="ns" data-lv="{level}">')
    parts.append(node_card_html(node, level, colors))

    children = node.get("children", [])
    if children:
        child_items = "".join(
            render_subtree(child, level + 1, colors)
            for child in children
        )
        all_leaves = not any(c.get("children") for c in children)
        vert = " cg-vertical" if (level >= 2 and all_leaves and len(children) > 4) else ""
        parts.append(f'<div class="cg{vert}">{child_items}</div>')

    parts.append("</div>")
    return "".join(parts)


def generate_html(data: dict[str, Any], colors: dict[str, Any], bg_override: str | None = None) -> str:
    """Generate the complete standalone HTML document."""
    total = get_tree_depth(data)
    body = render_subtree(data, 0, colors)
    page_bg = bg_override if bg_override else colors["bg"]
    title = html_mod.escape(data.get("name", "Org Chart"))
    subtitle = html_mod.escape(data.get("description", ""))
    line_color = colors["line_color"]

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
  background: {page_bg};
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
}}
.chart-title {{
  font-size: 26px; font-weight: 700; color: #1a1a2e;
  margin-top: 40px; letter-spacing: 1px;
}}
.chart-sub {{ font-size: 13px; color: #aaa; margin-bottom: 30px; }}
.main-container {{
  position: relative;
  width: calc(100% - 60px);
  max-width: 1500px;
  overflow: visible;
  padding: 0 0 40px 0;
}}
svg#lines {{
  position: absolute; left: 0; top: 0;
  width: 100%; height: 100%;
  z-index: 0; pointer-events: none;
}}
.ns {{ display: flex; flex-direction: column; align-items: center; min-width: 80px; }}
.cg {{ display: flex; justify-content: space-evenly; align-items: flex-start; gap: 10px; flex-wrap: nowrap; margin-top: 60px; width: 100%; }}
.cg-vertical {{ flex-direction: column; align-items: center; gap: 6px; width: auto; border: 1.5px solid {line_color}; border-radius: 10px; padding: 10px 14px; }}
.nc {{ transition: transform .2s, box-shadow .2s; }}
.nc:hover {{
  transform: translateY(-2px);
  box-shadow: 0 4px 22px rgba(0,0,0,.1) !important;
}}
.nn {{ font-size: 15px; font-weight: 700; }}
.nl-filled, .nl-empty {{ font-size: 12px; margin-top: 4px; }}
.nl-filled {{ font-weight: 500; }}
.nl-empty {{ font-weight: 400; font-style: italic; }}
.nr {{
  font-size: 10px; margin-top: 7px; line-height: 1.5;
  padding-top: 6px; border-top: 1px solid rgba(0,0,0,.06);
}}
.nt {{
  display: inline-block; font-size: 10px;
  padding: 2px 8px; border-radius: 4px; margin: 3px 2px 0;
}}
.nt-wrap {{ margin-top: 4px; }}
.footer {{ margin-top: 40px; font-size: 12px; color: #ccc; padding-bottom: 24px; }}
</style>
</head>
<body>

<div class="chart-title">{title}</div>
<div class="chart-sub">{subtitle}</div>

<div class="main-container" id="mainContainer">
<svg id="lines"></svg>
{body}
</div>

<div class="footer">Org Chart Generator</div>

<script>
(function() {{
  function equalizeNonLeaves() {{
    var groups = {{}};
    document.querySelectorAll('.ns').forEach(function(ns) {{
      // Only process non-leaf nodes (those with children)
      if (!ns.querySelector(':scope > .cg')) return;
      var nc = ns.querySelector(':scope > .nc');
      if (!nc) return;
      var lv = ns.getAttribute('data-lv') || '0';
      if (!groups[lv]) groups[lv] = [];
      groups[lv].push(nc);
    }});
    Object.keys(groups).forEach(function(lv) {{
      var maxH = 0;
      groups[lv].forEach(function(nc) {{ maxH = Math.max(maxH, nc.offsetHeight); }});
      groups[lv].forEach(function(nc) {{ nc.style.height = maxH + 'px'; }});
    }});
  }}

  function drawLines() {{
    equalizeNonLeaves();
    var svg = document.getElementById('lines');
    var mc = document.getElementById('mainContainer');
    var mRect = mc.getBoundingClientRect();

    var allCards = document.querySelectorAll('.nc');
    var maxRight = 0;
    allCards.forEach(function(c) {{
      var r = c.getBoundingClientRect();
      var right = r.right - mRect.left;
      if (right > maxRight) maxRight = right;
    }});
    var W = Math.max(mRect.width, maxRight + 20);
    var H = mc.scrollHeight;
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    svg.style.height = H + 'px';

    var pathParts = [];
    var allNS = document.querySelectorAll('.ns');

    allNS.forEach(function(parentNS) {{
      var cg = parentNS.querySelector(':scope > .cg');
      if (!cg) return;
      var childrenNS = cg.querySelectorAll(':scope > .ns');
      if (!childrenNS.length) return;
      var isVert = cg.classList.contains('cg-vertical');

      var parentCard = parentNS.querySelector(':scope > .nc');
      if (!parentCard) return;
      var pr = parentCard.getBoundingClientRect();
      var parentCX = pr.left + pr.width / 2 - mRect.left;
      var parentBY = pr.bottom - mRect.top;

      var childData = [];
      for (var i = 0; i < childrenNS.length; i++) {{
        var childCard = childrenNS[i].querySelector(':scope > .nc');
        if (!childCard) continue;
        var cr = childCard.getBoundingClientRect();
        childData.push({{
          cx: cr.left + cr.width / 2 - mRect.left,
          cy: cr.top - mRect.top,
        }});
      }}
      if (!childData.length) return;

      if (isVert) {{
        var boxRect = cg.getBoundingClientRect();
        var boxCX = boxRect.left + boxRect.width / 2 - mRect.left;
        var boxTY = boxRect.top - mRect.top;
        pathParts.push('M ' + parentCX + ' ' + parentBY + ' L ' + parentCX + ' ' + boxTY);
        pathParts.push('M ' + parentCX + ' ' + boxTY + ' L ' + boxCX + ' ' + boxTY);
      }} else {{
        var hLineY = (parentBY + childData[0].cy) / 2;
        var minCX = childData[0].cx;
        var maxCX = childData[childData.length - 1].cx;
        pathParts.push('M ' + minCX + ' ' + hLineY + ' L ' + maxCX + ' ' + hLineY);
        for (var j = 0; j < childData.length; j++) {{
          pathParts.push('M ' + childData[j].cx + ' ' + hLineY + ' L ' + childData[j].cx + ' ' + childData[j].cy);
        }}
        pathParts.push('M ' + parentCX + ' ' + parentBY + ' L ' + parentCX + ' ' + hLineY);
      }}
    }});

    if (pathParts.length) {{
      svg.innerHTML = '<path d="' + pathParts.join('') + '" stroke="{line_color}" stroke-width="2" fill="none"/>';
    }}
  }}

  window.addEventListener('load', function() {{ setTimeout(drawLines, 100); }});
  window.addEventListener('resize', function() {{
    clearTimeout(window.__dt);
    window.__dt = setTimeout(drawLines, 150);
  }});
}})();
</script>

</body>
</html>"""


def _mermaid_sanitize(text: str) -> str:
    """Escape characters that break Mermaid label parsing."""
    return (
        text.replace('"', "'")
        .replace("#", " ")
        .replace(";", ",")
        .replace("[", "(")
        .replace("]", ")")
    )


def generate_mermaid(data: dict[str, Any]) -> str:
    """Generate a Mermaid flowchart (vertical top-to-bottom)."""
    lines = ["graph TB"]
    counter = [0]

    def walk(node, parent_id):
        nid = f"N{counter[0]}"
        counter[0] += 1
        name = _mermaid_sanitize(node.get("name", ""))
        leader = node.get("leader", "") or ""
        resp = " - ".join(node.get("responsibilities", []))
        meta = node.get("meta", {})

        label_parts = [name]
        if leader and leader not in VACANT_MARKERS:
            label_parts.append(_mermaid_sanitize(leader))
        if resp:
            label_parts.append(_mermaid_sanitize(resp))
        if meta:
            meta_str = " | ".join(
                f"{_mermaid_sanitize(k)}:{_mermaid_sanitize(v)}"
                for k, v in meta.items()
            )
            label_parts.append(meta_str)

        label = "<br/>".join(label_parts)
        lines.append(f'    {nid}["{label}"]')
        if parent_id is not None:
            lines.append(f"    {parent_id} --> {nid}")
        for child in node.get("children", []):
            walk(child, nid)
        return nid

    walk(data, None)
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Org chart generator (HTML / Mermaid / PPTX)")
    parser.add_argument("input", help="Path to JSON data file")
    parser.add_argument("-o", "--output", default="org_chart.html", help="Output file path")
    parser.add_argument(
        "-f", "--format", choices=["html", "mermaid", "pptx"], default="html",
        help="Output format (default: html)",
    )
    parser.add_argument(
        "--colors", choices=list(COLOR_SCHEMES.keys()), default="tech-blue",
        help="Color scheme (default: tech-blue)",
    )
    parser.add_argument(
        "--bg", default=None,
        help="Override page background color (e.g. FFFFFF for white)",
    )
    args = parser.parse_args()

    data = load_json(args.input)
    depth = get_tree_depth(data)

    if args.format == "mermaid":
        md = generate_mermaid(data)
        out = Path(args.output)
        out.write_text(md, encoding="utf-8")
        print(f"Generated: {out}")
        print(f"  format: mermaid  levels: {depth}")

    elif args.format == "pptx":
        colors = COLOR_SCHEMES[args.colors]
        html_content = generate_html(data, colors, bg_override="#FFFFFF")
        html_path = Path(args.output).with_suffix(".html")
        html_path.write_text(html_content, encoding="utf-8")
        print(f"Generated HTML (white bg): {html_path}")
        pptx_path = Path(args.output)
        screenshot.main(str(html_path), str(pptx_path))

    else:
        colors = COLOR_SCHEMES[args.colors]
        html_content = generate_html(data, colors, bg_override=args.bg)
        Path(args.output).write_text(html_content, encoding="utf-8")
        print(f"Generated: {args.output}")
        print(f"  format: html  colors: {args.colors}  levels: {depth}")


if __name__ == "__main__":
    main()
