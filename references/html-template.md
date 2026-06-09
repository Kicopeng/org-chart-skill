# HTML 组织架构图模板

## 核心架构

三层结构：**flexbox 流式布局卡片** + **SVG 绝对定位画线** + **JS 精确坐标计算**。

```
<div class="main-container">     ← position: relative
  <svg id="lines">               ← position: absolute; z-index: 0; 画线层
  <div class="root-section">     ← 根节点 (z-index: 1)
  <div class="dept-row">         ← 子节点 flex 均匀分布 (z-index: 1, margin-top: 60px)
</div>
```

## CSS 关键规则

```css
.main-container {
  position: relative;
  width: calc(100% - 60px);
  max-width: 1400px;
  overflow: visible;
}
svg#lines {
  position: absolute; top: 0; left: 0;
  width: 100%; height: 100%;
  z-index: 0;
  pointer-events: none;  /* 穿透点击 */
}
.dept-row {
  display: flex;
  justify-content: space-evenly;  /* 均匀分布 */
  margin-top: 60px;              /* 层级间隔 */
  position: relative;
  z-index: 1;
}
```

## 节点卡片样式

```css
/* 根节点 - 深蓝渐变 */
.root-card {
  background: linear-gradient(145deg, #1a1a2e, #16213e);
  color: #fff;
  border-radius: 16px;
  padding: 22px 64px;
  text-align: center;
}

/* 子节点 - 白色 */
.dept-card {
  background: #fff;
  border-radius: 12px;
  padding: 18px 12px;
  min-width: 96px;
  text-align: center;
  box-shadow: 0 2px 14px rgba(0,0,0,.05);
  border: 1px solid #eee;
}

/* 中层节点 (3层+) - 浅蓝 */
.mid-card {
  background: #3a7bd5;
  color: #fff;
  border-radius: 14px;
  padding: 18px 24px;
}
```

## JS 画线核心逻辑

```javascript
function drawLines() {
  // 1. 获取容器边界
  var mRect = mainContainer.getBoundingClientRect();

  // 2. 根节点底部中位
  var rRect = rootSection.getBoundingClientRect();
  var rootCX = rRect.left + rRect.width / 2 - mRect.left;
  var rootBY = rRect.bottom - mRect.top;

  // 3. 各子节点顶部中位 (相对容器)
  var depts = [];
  deptItems.forEach(function(item) {
    var card = item.querySelector('.dept-card');
    var cRect = card.getBoundingClientRect();
    depts.push({
      cx: cRect.left + cRect.width / 2 - mRect.left,
      cy: cRect.top - mRect.top
    });
  });

  // 4. 横线 Y = 根底与子顶的正中间
  var hLineY = (rootBY + depts[0].cy) / 2;

  // 5. 构建 SVG path
  var minX = depts[0].cx;
  var maxX = depts[depts.length-1].cx;
  var path = '';

  // 横线 (左一到右一)
  path += 'M ' + minX + ' ' + hLineY + ' L ' + maxX + ' ' + hLineY;

  // 各竖线 (横线→子节点顶部)
  depts.forEach(function(d) {
    path += ' M ' + d.cx + ' ' + hLineY + ' L ' + d.cx + ' ' + d.cy;
  });

  // 根竖线 (根底→横线)
  path += ' M ' + rootCX + ' ' + rootBY + ' L ' + rootCX + ' ' + hLineY;

  // 6. 注入 SVG
  svg.setAttribute('viewBox', '0 0 ' + mRect.width + ' ' + mainContainer.scrollHeight);
  svg.innerHTML = '<path d="' + path + '" stroke="#c0c4cc" stroke-width="2" fill="none"/>';
}

// 7. 在 load 后延迟执行，确保布局计算完毕
window.addEventListener('load', function() { setTimeout(drawLines, 80); });
```

## 关键要点

- **z-index 分层**：SVG 线层(z-index:0) 在内容卡片(z-index:1) 之后，线不会遮住卡片
- **pointer-events: none**：用户可正常点击卡片，不受 SVG 遮挡
- **getBoundingClientRect()**：获取实际像素坐标，不用估算
- **横线中位计算**：`(rootBY + firstDeptCY) / 2` 精确居中
- **延迟执行**：`setTimeout(drawLines, 80)` 确保浏览器渲染完成后再测量坐标
- **window.load 非 DOMContentLoaded**：需要等所有资源（字体/图片）加载，布局更稳定
- **space-evenly**：子节点自动均匀分布，无需手动计算间距

## 多层级扩展

当超过 2 层时，递归处理：

1. 每对父子层之间用 `margin-top: 60px` 分隔
2. 每个层级组独立画线（复用同一逻辑）
3. 外层容器用 `flex-direction: column` 纵向堆叠
4. 中层卡片用浅色背景（见配色规则）

## 附加信息展示

若数据包含司龄、绩效、职务等额外字段，以小标签形式展示：

```html
<span class="d-tag">司龄 3年</span>
<span class="d-tag">绩效 A</span>
<span class="d-tag">总监</span>
```
```css
.d-tag {
  display: inline-block; font-size: 10px; color: #888;
  background: #f4f5f9; padding: 2px 8px;
  border-radius: 4px; margin-top: 5px;
}
```
