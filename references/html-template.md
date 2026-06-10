# HTML Org Chart Template

## Architecture

Three layers: **flexbox card layout** + **SVG absolute positioning for lines** + **JS coordinate measurement**.

```
<div class="main-container">     # position: relative; overflow: visible
  <svg id="lines">               # position: absolute; z-index: 0; pointer-events: none
  <div class="ns" data-lv="0">   # position: relative; z-index: 1 (cards float above SVG)
    <div class="nc">...card...</div>
    <div class="cg">children...</div>
  </div>
</div>
```

## Key CSS

```css
.ns { flex column, center-aligned, position:relative z-index:1 }
.nc { rounded rect, transitions for hover }
.cg { flex row, center, gap:10px, margin-top:60px, width:100% }
.cg[data-leaf="true"] { flex-wrap: wrap; row-gap: 10px }  /* wraps to multiple rows */
```

## Line Drawing (JS)

1. `equalizeNonLeaves()` — set all non-leaf `.nc` cards to max height per level (ensures same-level alignment)
2. Measure all `.nc` cards via `getBoundingClientRect()` relative to `mainContainer`
3. For each parent-child group: draw H-line at midpoint, vertical drops to each child, vertical from parent to H-line
4. H-line span is computed by scanning all children for actual min/max X (handles wrapped rows)
5. SVG viewBox auto-expands to cover overflowed content (`maxRight + 20`)

## CSS Class Reference

| Class | Purpose |
|-------|---------|
| `.ns` | Node subtree wrapper (card + children group) |
| `.nc` | Node card (rounded rectangle) |
| `.cg` | Children group (flex row) |
| `.nn` | Node name (bold title) |
| `.nl-filled` | Leader name when filled |
| `.nl-empty` | Leader name when vacant |
| `.nr` | Responsibilities text |
| `.nt` | Meta tag (tenure, performance, etc.) |
