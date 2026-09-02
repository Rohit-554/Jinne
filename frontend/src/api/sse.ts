export interface ParsedSSEEvent {
  event: string
  data: string
}

/** Parses one raw SSE event block ("event: x\ndata: y") into its parts.
 * Returns null for a block with no data line. */
export function parseSSEEvent(rawEvent: string): ParsedSSEEvent | null {
  let event = 'message'
  let data = ''
  let hasData = false

  for (const line of rawEvent.split('\n')) {
    if (line.startsWith('event:')) {
      event = line.slice('event:'.length).trim()
    } else if (line.startsWith('data:')) {
      data = line.slice('data:'.length).trim()
      hasData = true
    }
  }

  return hasData ? { event, data } : null
}

/** Splits a growing SSE buffer into complete "\n\n"-terminated event
 * blocks, returning the parsed events found and the leftover buffer. */
export function extractSSEEvents(buffer: string): { events: ParsedSSEEvent[]; remainder: string } {
  const events: ParsedSSEEvent[] = []
  let remainder = buffer
  let boundary = remainder.indexOf('\n\n')

  while (boundary !== -1) {
    const rawEvent = remainder.slice(0, boundary)
    remainder = remainder.slice(boundary + 2)
    const parsed = parseSSEEvent(rawEvent)
    if (parsed) events.push(parsed)
    boundary = remainder.indexOf('\n\n')
  }

  return { events, remainder }
}
