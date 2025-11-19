/**
 * Smart event data adapter for handling multiple data formats
 *
 * This adapter provides a flexible way to extract data from events that may
 * come in different formats from the Python backend. It handles common
 * variations and provides fallbacks to prevent data format mismatches.
 *
 * @example
 * ```typescript
 * // Extract array from various formats
 * const nodes = EventDataAdapter.extractArray<MayaNode>(data, 'nodes', 'value')
 * // Handles: [node1, node2]
 * // Handles: {nodes: [node1, node2]}
 * // Handles: {value: [node1, node2]}
 *
 * // Extract string from various formats
 * const name = EventDataAdapter.extractString(data, 'node', 'name')
 * // Handles: "pSphere1"
 * // Handles: {node: "pSphere1"}
 * // Handles: {name: "pSphere1"}
 * ```
 */
export class EventDataAdapter {
  /**
   * Extract array data from various formats
   *
   * @param data - Raw event data (can be array or object)
   * @param possibleKeys - Keys to try when data is an object (in priority order)
   * @returns Extracted array or empty array if extraction fails
   *
   * @example
   * ```typescript
   * // Direct array
   * extractArray([1, 2, 3]) // → [1, 2, 3]
   *
   * // Object with specific key
   * extractArray({nodes: [1, 2, 3]}, 'nodes') // → [1, 2, 3]
   *
   * // Object with fallback keys
   * extractArray({value: [1, 2, 3]}, 'nodes', 'value') // → [1, 2, 3]
   * ```
   */
  static extractArray<T>(data: unknown, ...possibleKeys: string[]): T[] {
    // Case 1: Direct array
    if (Array.isArray(data)) {
      return data as T[]
    }

    // Case 2: Object with array field
    if (data && typeof data === 'object') {
      const obj = data as Record<string, unknown>

      // Try each specified key in order
      for (const key of possibleKeys) {
        if (key in obj && Array.isArray(obj[key])) {
          return obj[key] as T[]
        }
      }

      // Fallback: try common keys
      const commonKeys = ['value', 'data', 'items', 'nodes', 'list', 'results']
      for (const key of commonKeys) {
        if (key in obj && Array.isArray(obj[key])) {
          return obj[key] as T[]
        }
      }
    }

    return []
  }

  /**
   * Extract string value from various formats
   *
   * @param data - Raw event data (can be string or object)
   * @param possibleKeys - Keys to try when data is an object (in priority order)
   * @returns Extracted string or empty string if extraction fails
   *
   * @example
   * ```typescript
   * // Direct string
   * extractString("hello") // → "hello"
   *
   * // Object with specific key
   * extractString({node: "pSphere1"}, 'node') // → "pSphere1"
   *
   * // Object with fallback keys
   * extractString({name: "pSphere1"}, 'node', 'name') // → "pSphere1"
   * ```
   */
  static extractString(data: unknown, ...possibleKeys: string[]): string {
    // Case 1: Direct string
    if (typeof data === 'string') {
      return data
    }

    // Case 2: Object with string field
    if (data && typeof data === 'object') {
      const obj = data as Record<string, unknown>

      // Try each specified key in order
      for (const key of possibleKeys) {
        if (key in obj && typeof obj[key] === 'string') {
          return obj[key] as string
        }
      }

      // Fallback: try common keys
      const commonKeys = ['value', 'data', 'name', 'id', 'text']
      for (const key of commonKeys) {
        if (key in obj && typeof obj[key] === 'string') {
          return obj[key] as string
        }
      }
    }

    return ''
  }

  /**
   * Extract object value from various formats
   *
   * @param data - Raw event data
   * @param possibleKeys - Keys to try when data is nested
   * @returns Extracted object or empty object if extraction fails
   */
  static extractObject<T extends Record<string, unknown>>(data: unknown, ...possibleKeys: string[]): T {
    // Case 1: Direct object
    if (data && typeof data === 'object' && !Array.isArray(data)) {
      // If no keys specified, return the object directly
      if (possibleKeys.length === 0) {
        return data as T
      }

      const obj = data as Record<string, unknown>

      // Try each specified key
      for (const key of possibleKeys) {
        if (key in obj && typeof obj[key] === 'object' && !Array.isArray(obj[key])) {
          return obj[key] as T
        }
      }
    }

    return {} as T
  }
}
