export type MemoryStatus = 'ACTIVE' | 'SUPERSEDED' | 'UNCERTAIN' | 'EXPIRED'

export interface MemorySummary {
  id: number
  type: string
  subject: string
  relation: string
  value: string
  status: MemoryStatus
  importance: number
  confidence: number
}
