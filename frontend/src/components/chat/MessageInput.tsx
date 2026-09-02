import { Send } from 'lucide-react'
import { useState } from 'react'
import type { FormEvent } from 'react'

interface MessageInputProps {
  onSend: (message: string) => void
  disabled: boolean
}

export function MessageInput({ onSend, disabled }: MessageInputProps) {
  const [value, setValue] = useState('')

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue('')
  }

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-2 border-t border-border px-6 py-4">
      <input
        type="text"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="Message Mira..."
        disabled={disabled}
        className="flex-1 rounded-md border border-border bg-surface px-3 py-2 text-sm text-text placeholder:text-text-secondary focus:outline-none focus:ring-1 focus:ring-accent disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={disabled || !value.trim()}
        className="flex items-center justify-center rounded-md bg-accent px-3 py-2 text-bg disabled:opacity-40"
        aria-label="Send message"
      >
        <Send size={16} />
      </button>
    </form>
  )
}
