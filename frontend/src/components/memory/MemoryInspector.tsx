import { useQuery } from '@tanstack/react-query'
import { ChevronRight, PanelRightClose } from 'lucide-react'
import { useState } from 'react'
import { fetchMemories } from '../../api/client'

interface MemoryInspectorProps {
  refreshToken: number
}

export function MemoryInspector({ refreshToken }: MemoryInspectorProps) {
  const [open, setOpen] = useState(true)

  const { data: memories, isLoading, isError } = useQuery({
    queryKey: ['memories', refreshToken],
    queryFn: fetchMemories,
  })

  if (!open) {
    return (
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="flex items-center gap-1 border-l border-border px-2 text-text-secondary hover:text-text"
        aria-label="Open memory inspector"
      >
        <ChevronRight size={16} />
      </button>
    )
  }

  return (
    <div className="flex w-[320px] flex-col border-l border-border">
      <div className="flex items-center justify-between border-b border-border px-4 py-4">
        <h2 className="text-sm font-semibold text-text">Memory Inspector</h2>
        <button
          type="button"
          onClick={() => setOpen(false)}
          className="text-text-secondary hover:text-text"
          aria-label="Collapse memory inspector"
        >
          <PanelRightClose size={16} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4">
        {isLoading && <p className="text-sm text-text-secondary">Loading memories...</p>}
        {isError && <p className="text-sm text-error">Couldn't reach the companion engine.</p>}
        {memories && memories.length === 0 && (
          <div className="text-sm text-text-secondary">
            No long-term memories yet.
            <br />
            Important facts from your conversations will appear here.
          </div>
        )}
        {memories && memories.length > 0 && (
          <ul className="flex flex-col gap-3">
            {memories.map((memory) => (
              <li
                key={memory.id}
                className="rounded-md border border-border bg-surface px-3 py-2 text-sm"
              >
                <div className="font-mono text-xs text-accent">{memory.type}</div>
                <div className="text-text">{memory.value}</div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
