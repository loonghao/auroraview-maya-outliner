/**
 * Responsive Scale Composable
 * 
 * Automatically calculates and applies optimal zoom scale based on window size.
 * Uses intelligent breakpoints to ensure UI remains usable across different window sizes.
 */

import { ref, onMounted, onUnmounted, computed } from 'vue'

export interface ScaleConfig {
  /** Base width for 100% scale (default: 800px) */
  baseWidth?: number
  /** Base height for 100% scale (default: 600px) */
  baseHeight?: number
  /** Minimum scale factor (default: 0.6 = 60%) */
  minScale?: number
  /** Maximum scale factor (default: 1.5 = 150%) */
  maxScale?: number
  /** Enable smooth transitions (default: true) */
  smoothTransition?: boolean
  /** Throttle delay in ms for resize events (default: 16ms ≈ 60fps) */
  throttleDelay?: number
}

export function useResponsiveScale(config: ScaleConfig = {}) {
  const {
    baseWidth = 800,
    baseHeight = 600,
    minScale = 0.6,
    maxScale = 1.5,
    throttleDelay = 16 // ~60fps for smooth updates
  } = config

  const windowWidth = ref(window.innerWidth)
  const windowHeight = ref(window.innerHeight)
  const scale = ref(1)
  const isResizing = ref(false) // Track if currently resizing

  /**
   * Calculate optimal scale based on window dimensions
   * Only scales DOWN when window is smaller than base size
   * Never scales UP - let content use natural responsive layout
   */
  const calculateScale = () => {
    const widthRatio = windowWidth.value / baseWidth
    const heightRatio = windowHeight.value / baseHeight

    // Use the smaller ratio to ensure content fits in both dimensions
    let calculatedScale = Math.min(widthRatio, heightRatio)

    // Only scale down, never scale up (max scale is 1.0)
    // This prevents content from being magnified when window is larger
    calculatedScale = Math.max(minScale, Math.min(1.0, calculatedScale))

    // Round to 2 decimal places for cleaner values
    return Math.round(calculatedScale * 100) / 100
  }

  let lastResizeTime = 0
  let rafId: number | null = null
  let resizeEndTimeout: number | null = null

  /**
   * Throttled resize handler using requestAnimationFrame for smooth 60fps updates
   * This ensures resize updates are synchronized with browser repaints
   */
  const handleResize = () => {
    const now = Date.now()

    // Mark as resizing
    isResizing.value = true

    // Clear resize end timeout
    if (resizeEndTimeout) {
      clearTimeout(resizeEndTimeout)
    }

    // Throttle: only update if enough time has passed
    if (now - lastResizeTime < throttleDelay) {
      // Schedule update for next frame if not already scheduled
      if (!rafId) {
        rafId = requestAnimationFrame(() => {
          rafId = null
          handleResize()
        })
      }
      return
    }

    lastResizeTime = now

    // Update immediately for smooth animation
    const oldScale = scale.value
    windowWidth.value = window.innerWidth
    windowHeight.value = window.innerHeight
    scale.value = calculateScale()

    // Only log significant scale changes (reduce console spam)
    if (Math.abs(oldScale - scale.value) > 0.05) {
      console.log(`[useResponsiveScale] Scale changed: ${oldScale.toFixed(2)} → ${scale.value.toFixed(2)} (${windowWidth.value}x${windowHeight.value})`)
    }

    // Mark resize as ended after 150ms of no resize events
    resizeEndTimeout = window.setTimeout(() => {
      isResizing.value = false
    }, 150)
  }

  onMounted(() => {
    // Initial calculation
    scale.value = calculateScale()

    // Listen for window resize
    window.addEventListener('resize', handleResize)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
    if (rafId) {
      cancelAnimationFrame(rafId)
    }
    if (resizeEndTimeout) {
      clearTimeout(resizeEndTimeout)
    }
  })

  /**
   * CSS style for scaling
   *
   * NOTE: Using CSS zoom for now. If performance issues occur, can switch back to transform.
   *
   * Zoom approach (current):
   * - Simpler rendering pipeline
   * - No transform matrix calculations
   * - May cause issues in some WebView2 versions
   *
   * Transform approach (fallback):
   * - More compatible
   * - Requires width/height adjustment
   * - May cause layer promotion flashing
   */
  const scaleStyle = computed(() => {
    const baseStyle: Record<string, any> = {
      width: '100%',
      height: '100%',
      // Disable transitions to prevent flashing
      transition: 'none',
      // Anti-aliasing
      WebkitFontSmoothing: 'subpixel-antialiased',
      MozOsxFontSmoothing: 'grayscale',
      textRendering: 'optimizeLegibility',
      imageRendering: '-webkit-optimize-contrast',
      // GPU acceleration (minimal)
      backfaceVisibility: 'hidden',
    }

    if (scale.value >= 1.0) {
      // No scaling needed
      return baseStyle
    }

    // OPTION 1: CSS zoom (current - simpler but may cause issues)
    return {
      ...baseStyle,
      zoom: scale.value,
    }

    // OPTION 2: Transform (fallback - uncomment if zoom causes problems)
    // return {
    //   ...baseStyle,
    //   transform: `scale(${scale.value})`,
    //   transformOrigin: 'top left',
    //   width: `${100 / scale.value}%`,
    //   height: `${100 / scale.value}%`,
    // }
  })

  /**
   * Get current scale percentage (e.g., 80 for 80%)
   */
  const scalePercentage = computed(() => Math.round(scale.value * 100))

  /**
   * Check if currently scaled down
   */
  const isScaledDown = computed(() => scale.value < 1)

  /**
   * Check if currently scaled up
   */
  const isScaledUp = computed(() => scale.value > 1)

  /**
   * Manually set scale (useful for user controls)
   */
  const setScale = (newScale: number) => {
    scale.value = Math.max(minScale, Math.min(maxScale, newScale))
  }

  /**
   * Reset to auto-calculated scale
   */
  const resetScale = () => {
    scale.value = calculateScale()
  }

  /**
   * Update window dimensions and recalculate scale
   * Optimized for zero-latency updates to prevent flashing
   */
  const updateDimensions = (width: number, height: number) => {
    const oldScale = scale.value

    // Update dimensions immediately (no throttling for backend events)
    windowWidth.value = width
    windowHeight.value = height

    // Calculate new scale
    const newScale = calculateScale()

    // Only log if scale actually changed (reduce console spam)
    if (Math.abs(newScale - oldScale) > 0.01) {
      scale.value = newScale
      console.log(`[useResponsiveScale] Scale changed: ${oldScale.toFixed(2)} → ${newScale.toFixed(2)} (${width}x${height})`)
    } else {
      // Scale didn't change, just update silently
      scale.value = newScale
    }
  }

  return {
    scale,
    scaleStyle,
    scalePercentage,
    isScaledDown,
    isScaledUp,
    isResizing,
    setScale,
    resetScale,
    updateDimensions,
    windowWidth,
    windowHeight
  }
}

