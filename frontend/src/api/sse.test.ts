import { describe, expect, it } from 'vitest'
import { extractSSEEvents, parseSSEEvent } from './sse'

describe('parseSSEEvent', () => {
  it('parses event type and data', () => {
    const result = parseSSEEvent('event: chunk\ndata: {"text":"hi"}')
    expect(result).toEqual({ event: 'chunk', data: '{"text":"hi"}' })
  })

  it('defaults to "message" when no event line is present', () => {
    const result = parseSSEEvent('data: hello')
    expect(result).toEqual({ event: 'message', data: 'hello' })
  })

  it('returns null when there is no data line', () => {
    expect(parseSSEEvent('event: chunk')).toBeNull()
  })
})

describe('extractSSEEvents', () => {
  it('extracts complete events and keeps an incomplete trailing block as remainder', () => {
    const buffer = 'event: chunk\ndata: {"text":"a"}\n\nevent: chunk\ndata: {"text":"b"}\n\nevent: don'
    const { events, remainder } = extractSSEEvents(buffer)

    expect(events).toEqual([
      { event: 'chunk', data: '{"text":"a"}' },
      { event: 'chunk', data: '{"text":"b"}' },
    ])
    expect(remainder).toBe('event: don')
  })

  it('returns no events and the full buffer as remainder when nothing is complete yet', () => {
    const { events, remainder } = extractSSEEvents('event: chunk\ndata: partial')
    expect(events).toEqual([])
    expect(remainder).toBe('event: chunk\ndata: partial')
  })

  it('handles a full done event with JSON metadata', () => {
    const buffer = 'event: done\ndata: {"retrieved_memories":[],"created_memories":[],"updated_memories":[]}\n\n'
    const { events, remainder } = extractSSEEvents(buffer)

    expect(events).toHaveLength(1)
    expect(events[0].event).toBe('done')
    expect(remainder).toBe('')
  })
})
