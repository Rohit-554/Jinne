import type { MemorySummary } from './memory'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
}

export interface ChatTurnMetadata {
  retrieved_memories: MemorySummary[]
  created_memories: MemorySummary[]
  updated_memories: MemorySummary[]
}
