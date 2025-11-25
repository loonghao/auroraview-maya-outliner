# 响应式自动缩放功能

## 功能概述

Maya Outliner 现在支持**智能响应式缩放**，根据窗口大小自动调整 UI 缩放比例，确保在不同窗口尺寸下都能获得最佳的用户体验。

## 工作原理

### 智能缩放算法

```typescript
// 计算缩放比例
const widthRatio = windowWidth / baseWidth   // 宽度比例
const heightRatio = windowHeight / baseHeight // 高度比例

// 使用较小的比例，确保内容完全可见
const scale = Math.min(widthRatio, heightRatio)

// 应用约束
scale = Math.max(minScale, Math.min(maxScale, scale))
```

### 缩放策略

1. **基准尺寸**：800x600 (设计基准)
2. **最小缩放**：50% (确保小窗口可用)
3. **最大缩放**：150% (避免过度放大)
4. **平滑过渡**：200ms 缓动动画

## 配置参数

### 默认配置

```typescript
const { scaleStyle, scalePercentage, isScaledDown } = useResponsiveScale({
  baseWidth: 800,        // 基准宽度 (px)
  baseHeight: 600,       // 基准高度 (px)
  minScale: 0.5,         // 最小缩放 (50%)
  maxScale: 1.5,         // 最大缩放 (150%)
  smoothTransition: true, // 平滑过渡
  debounceDelay: 100     // 防抖延迟 (ms)
})
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `baseWidth` | number | 800 | 100% 缩放时的基准宽度 |
| `baseHeight` | number | 600 | 100% 缩放时的基准高度 |
| `minScale` | number | 0.6 | 最小缩放比例 (0.5 = 50%) |
| `maxScale` | number | 1.5 | 最大缩放比例 (1.5 = 150%) |
| `smoothTransition` | boolean | true | 是否启用平滑过渡动画 |
| `debounceDelay` | number | 100 | 窗口调整防抖延迟 (毫秒) |

## 使用示例

### 基本用法

```vue
<script setup lang="ts">
import { useResponsiveScale } from './composables/useResponsiveScale'

const { scaleStyle, scalePercentage } = useResponsiveScale()
</script>

<template>
  <div class="app-wrapper">
    <div class="app-container" :style="scaleStyle">
      <!-- 你的内容 -->
    </div>
  </div>
</template>

<style scoped>
.app-wrapper {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}
</style>
```

### 显示缩放指示器

```vue
<template>
  <div class="app-wrapper">
    <div class="app-container" :style="scaleStyle">
      <!-- 内容 -->
    </div>
    
    <!-- 当缩小时显示缩放百分比 -->
    <div v-if="isScaledDown" class="scale-indicator">
      {{ scalePercentage }}%
    </div>
  </div>
</template>
```

## 缩放效果示例

### 不同窗口尺寸的缩放比例

| 窗口尺寸 | 宽度比 | 高度比 | 最终缩放 | 说明 |
|---------|--------|--------|----------|------|
| 400x300 | 0.5 | 0.5 | **50%** | 最小缩放 |
| 600x450 | 0.75 | 0.75 | **75%** | 中等缩放 |
| 800x600 | 1.0 | 1.0 | **100%** | 基准尺寸 |
| 1200x900 | 1.5 | 1.5 | **150%** | 最大缩放 |
| 1600x400 | 2.0 | 0.67 | **67%** | 宽屏窗口 |

### 视觉效果

```
小窗口 (400x300)          中等窗口 (800x600)        大窗口 (1200x900)
┌─────────────┐          ┌──────────────────┐      ┌────────────────────────┐
│ [50% zoom]  │          │  [100% zoom]     │      │   [150% zoom]          │
│             │          │                  │      │                        │
│  UI 缩小    │          │   UI 正常        │      │    UI 放大             │
│  保持可用   │          │   最佳体验       │      │    更易阅读            │
└─────────────┘          └──────────────────┘      └────────────────────────┘
```

## 技术实现

### CSS Transform 方案

使用 `transform: scale()` 而不是修改字体大小或元素尺寸：

**优点：**
- ✅ 性能优异（GPU 加速）
- ✅ 保持布局一致性
- ✅ 支持平滑动画
- ✅ 不影响原有 CSS

**实现：**
```css
.app-container {
  transform: scale(0.75);
  transform-origin: top left;
  width: 133.33%;  /* 100 / 0.75 */
  height: 133.33%;
}
```

### 响应式监听

```typescript
// 监听窗口大小变化
window.addEventListener('resize', handleResize)

// 防抖处理
const handleResize = debounce(() => {
  scale.value = calculateScale()
}, 100)
```

## 性能优化

1. **防抖处理**：100ms 延迟，避免频繁计算
2. **GPU 加速**：使用 `transform` 而非 `width/height`
3. **条件渲染**：缩放指示器仅在缩小时显示
4. **精度控制**：缩放值保留 2 位小数

## 浏览器兼容性

| 特性 | Chrome | Firefox | Safari | Edge |
|------|--------|---------|--------|------|
| `transform: scale()` | ✅ | ✅ | ✅ | ✅ |
| `transform-origin` | ✅ | ✅ | ✅ | ✅ |
| CSS transitions | ✅ | ✅ | ✅ | ✅ |

## 常见问题

### Q: 为什么不使用 CSS `zoom` 属性？
A: `zoom` 不是标准属性，浏览器支持不一致。`transform: scale()` 是标准方案，性能更好。

### Q: 缩放会影响鼠标事件吗？
A: 不会。通过调整容器尺寸 (`width: 100/scale%`)，确保鼠标事件正确映射。

### Q: 如何禁用自动缩放？
A: 设置 `minScale: 1` 和 `maxScale: 1` 即可固定为 100% 缩放。

## 参考资料

- [MDN: CSS transform](https://developer.mozilla.org/en-US/docs/Web/CSS/transform)
- [CSS Container Queries](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Container_Queries)
- [Responsive Design Best Practices 2025](https://web.dev/responsive-web-design-basics/)

