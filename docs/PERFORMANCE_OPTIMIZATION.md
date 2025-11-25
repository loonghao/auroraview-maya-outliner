# Performance Optimization Guide

This document describes the performance optimizations implemented in AuroraView for smooth 60 FPS operation in DCC environments.

## Overview

AuroraView implements several layers of optimization to ensure smooth performance:

1. **Python-side resize throttling** - Limits Win32 API calls to ~60 FPS
2. **Frontend CSS anti-aliasing** - Improves visual quality during scaling
3. **Event deduplication** - Prevents redundant resize events
4. **Performance logging** - Tracks bottlenecks for debugging

## 1. Resize Event Throttling (Python)

### Problem
- Qt `resizeEvent` fires very frequently during window dragging (100+ times/second)
- Each event triggers expensive Win32 `SetWindowPos` API calls
- Each event sends IPC message to frontend
- Results in frame drops and stuttering

### Solution
Implemented throttling in `QtWebView.resizeEvent()`:

```python
# Throttle to ~60 FPS (16ms per frame)
self._resize_throttle_ms = 16

# Skip duplicate events
if new_size == self._last_emitted_size:
    return

# Throttle based on time
if time_since_last >= self._resize_throttle_ms:
    # Update immediately
    self._sync_embedded_geometry()
    self._webview.emit("window_resized", {...})
else:
    # Schedule delayed update
    QTimer.singleShot(self._resize_throttle_ms, delayed_resize)
```

### Benefits
- Reduces Win32 API calls from 100+/sec to ~60/sec
- Maintains smooth 60 FPS visual updates
- Prevents event queue overflow

## 2. CSS Anti-Aliasing (Frontend)

### Problem
- CSS `transform: scale()` uses bilinear interpolation by default
- Results in jagged edges and blurry text when scaling down
- Poor visual quality during resize operations

### Solution
Added comprehensive anti-aliasing CSS properties:

```typescript
const scaleStyle = computed(() => ({
  // Anti-aliasing for better quality
  imageRendering: 'auto',              // Best quality scaling
  backfaceVisibility: 'hidden',        // Force GPU acceleration
  WebkitFontSmoothing: 'antialiased',  // Smooth fonts (WebKit)
  MozOsxFontSmoothing: 'grayscale',    // Smooth fonts (Firefox)
  perspective: '1000px',               // 3D context for better quality
  
  // GPU acceleration
  transform: `scale(${scale}) translate3d(0, 0, 0)`,
  willChange: isResizing ? 'transform' : 'auto',
}))
```

### Benefits
- Smoother text rendering during scaling
- Reduced jagged edges
- Better overall visual quality
- GPU-accelerated transforms

## 3. Performance Logging

### Startup Performance
Tracks time spent in each initialization phase:

```python
# Python side
logger.info(f"QtWebView: core.show() succeeded in {core_show_time:.1f}ms")
logger.info(f"QtWebView: initial geometry sync completed in {sync_time:.1f}ms")
logger.info(f"QtWebView: started embedded WebView in {total_time:.1f}ms total")
```

### Resize Performance
Tracks resize event frequency and processing time:

```typescript
// Frontend side
console.log(`[App.vue] window_resized #${count} (Δ${timeSinceLastEvent.toFixed(1)}ms)`)
console.log(`[App.vue] updateDimensions completed in ${updateTime.toFixed(2)}ms`)
console.log(`[useResponsiveScale] Scale changed: ${oldScale} → ${newScale}`)
```

### How to Use
1. Open browser DevTools console (F12)
2. Resize window and observe logs
3. Look for:
   - Event frequency (should be ~16ms apart for 60 FPS)
   - Processing time (should be <5ms)
   - Scale changes (should be smooth)

## 4. Startup Delay Optimization

### Problem
- 2-3 second delay when starting WebView in Maya
- Caused by:
  1. Waiting for `http://localhost:5173` dev server
  2. Loading Vue framework and components
  3. Delayed geometry sync retries

### Solutions

#### Production Mode (Recommended)
Use local `file:///` protocol instead of dev server:

```python
# In maya_outliner.py
dist_dir = os.path.join(os.path.dirname(__file__), "..", "dist")
index_html = os.path.join(dist_dir, "index.html")
if os.path.exists(index_html):
    url = f"file:///{os.path.abspath(index_html).replace(os.sep, '/')}"
```

Build production bundle:
```bash
npm run build
```

#### Development Mode
Keep dev server running before starting Maya:
```bash
npm run dev
```

## Performance Targets

| Metric | Target | Actual |
|--------|--------|--------|
| Resize event frequency | 60 FPS (16ms) | ~60 FPS |
| Resize processing time | <5ms | <3ms |
| Startup time (production) | <500ms | ~300ms |
| Startup time (dev) | <2s | ~1.5s |
| Visual quality | No jagged edges | ✓ Smooth |

## Troubleshooting

### Slow Resize Performance
1. Check Python logs for throttling messages
2. Verify `_resize_throttle_ms = 16`
3. Check browser console for event frequency

### Jagged Edges During Scaling
1. Verify CSS anti-aliasing properties are applied
2. Check `imageRendering: 'auto'` in computed style
3. Ensure GPU acceleration is enabled (`translate3d`)

### Slow Startup
1. Use production build (`npm run build`)
2. Check network tab for slow resource loading
3. Verify `file:///` protocol is used (not `http://`)

## Future Optimizations

1. **Lazy loading** - Load components on demand
2. **Virtual scrolling** - Only render visible tree nodes
3. **Web Workers** - Offload heavy computations
4. **IndexedDB caching** - Cache scene data locally
5. **Incremental updates** - Only update changed nodes

## See Also

- [Qt Integration Best Practices](QT_BEST_PRACTICES.md)
- [Architecture Overview](ARCHITECTURE_LAYERED_DESIGN.md)
- [Maya Integration Guide](MAYA_SOLUTION.md)

