import type { ChatMessage } from '../../types/chat'

interface ChatMessageListProps {
  messages: ChatMessage[]
  streamingContent: string | null
}

export function ChatMessageList({ messages, streamingContent }: ChatMessageListProps) {
  if (messages.length === 0 && streamingContent === null) {
    return (
      <div className="flex flex-1 items-center justify-center text-sm text-text-secondary">
        Say something to get started.
      </div>
    )
  }

  return (
    <div className="flex flex-1 flex-col gap-3 overflow-y-auto px-6 py-4">
      {messages.map((message) => (
        <MessageBubble key={message.id} role={message.role} content={message.content} />
      ))}
      {streamingContent !== null && <MessageBubble role="assistant" content={streamingContent} />}
    </div>
  )
}

function MessageBubble({ role, content }: { role: ChatMessage['role']; content: string }) {
  const isUser = role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[75%] rounded-lg px-4 py-2 text-sm whitespace-pre-wrap ${
          isUser ? 'bg-surface-secondary text-text' : 'bg-surface text-text border border-border'
        }`}
      >
        {content}
      </div>
    </div>
  )
}
