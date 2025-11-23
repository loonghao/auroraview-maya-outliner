/**
 * IndexedDB storage utility for persisting user preferences
 */

const DB_NAME = 'AuroraViewOutliner'
const DB_VERSION = 1
const STORE_NAME = 'preferences'

interface OutlinerPreferences {
  windowWidth?: number
  windowHeight?: number
  showDAGOnly?: boolean
  showHidden?: boolean
  expandedNodes?: string[]
  selectedNode?: string | null
}

class StorageManager {
  private db: IDBDatabase | null = null
  private initPromise: Promise<void> | null = null

  async init(): Promise<void> {
    if (this.db) return
    if (this.initPromise) return this.initPromise

    this.initPromise = new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION)

      request.onerror = () => {
        console.error('[Storage] Failed to open IndexedDB:', request.error)
        reject(request.error)
      }

      request.onsuccess = () => {
        this.db = request.result
        resolve()
      }

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result
        
        // Create object store if it doesn't exist
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          db.createObjectStore(STORE_NAME)
        }
      }
    })

    return this.initPromise
  }

  async get<K extends keyof OutlinerPreferences>(
    key: K
  ): Promise<OutlinerPreferences[K] | undefined> {
    await this.init()
    if (!this.db) return undefined

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(STORE_NAME, 'readonly')
      const store = transaction.objectStore(STORE_NAME)
      const request = store.get(key)

      request.onsuccess = () => resolve(request.result)
      request.onerror = () => {
        console.error(`[Storage] Failed to get ${String(key)}:`, request.error)
        reject(request.error)
      }
    })
  }

  async set<K extends keyof OutlinerPreferences>(
    key: K,
    value: OutlinerPreferences[K]
  ): Promise<void> {
    await this.init()
    if (!this.db) return

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(STORE_NAME, 'readwrite')
      const store = transaction.objectStore(STORE_NAME)
      const request = store.put(value, key)

      request.onsuccess = () => resolve()
      request.onerror = () => {
        console.error(`[Storage] Failed to set ${String(key)}:`, request.error)
        reject(request.error)
      }
    })
  }

  async getAll(): Promise<OutlinerPreferences> {
    await this.init()
    if (!this.db) return {}

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(STORE_NAME, 'readonly')
      const store = transaction.objectStore(STORE_NAME)
      const request = store.getAll()
      const keysRequest = store.getAllKeys()

      Promise.all([
        new Promise<any[]>((res, rej) => {
          request.onsuccess = () => res(request.result)
          request.onerror = () => rej(request.error)
        }),
        new Promise<IDBValidKey[]>((res, rej) => {
          keysRequest.onsuccess = () => res(keysRequest.result)
          keysRequest.onerror = () => rej(keysRequest.error)
        })
      ])
        .then(([values, keys]) => {
          const result: OutlinerPreferences = {}
          keys.forEach((key, index) => {
            result[key as keyof OutlinerPreferences] = values[index]
          })
          resolve(result)
        })
        .catch(reject)
    })
  }

  async clear(): Promise<void> {
    await this.init()
    if (!this.db) return

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(STORE_NAME, 'readwrite')
      const store = transaction.objectStore(STORE_NAME)
      const request = store.clear()

      request.onsuccess = () => resolve()
      request.onerror = () => {
        console.error('[Storage] Failed to clear:', request.error)
        reject(request.error)
      }
    })
  }
}

export const storage = new StorageManager()
export type { OutlinerPreferences }

