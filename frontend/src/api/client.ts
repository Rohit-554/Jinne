import { extractSSEEvents } from './sse'
import type { ChatTurnMetadata } from '../types/chat'
import type { MemorySummary } from '../types/memory'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

export async function fetchMemories(): Promise<MemorySummary[]> {
  const response = await fetch(`${API_BASE}/api/memories`)
  if (!response.ok) {
    throw new Error(`Failed to fetch memories: ${response.status}`)
  }
  const payload = (await response.json()) as { memories: MemorySummary[] }
  return payload.memories
}

export interface StreamChatCallbacks {
  onChunk: (text: string) => void
  onDone: (metadata: ChatTurnMetadata) => void
  onError: (message: string) => void
}

export async function streamChat(message: string, callbacks: StreamChatCallbacks): Promise<void> {
  let response: Response
  try {
    response = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    })
  } catch (err) {
    callbacks.onError(err instanceof Error ? err.message : 'Could not reach the companion engine.')
    return
  }

  if (!response.ok || !response.body) {
    callbacks.onError(`Chat request failed: ${response.status}`)
    return
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    const { events, remainder } = extractSSEEvents(buffer)
    buffer = remainder

    for (const { event, data } of events) {
      if (event === 'chunk') {
        callbacks.onChunk((JSON.parse(data) as { text: string }).text)
      } else if (event === 'done') {
        callbacks.onDone(JSON.parse(data) as ChatTurnMetadata)
      } else if (event === 'error') {
        callbacks.onError((JSON.parse(data) as { error: string }).error)
      }
    }
  }
}
