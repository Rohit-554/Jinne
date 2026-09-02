import { useState } from 'react'
import { streamChat } from '../api/client'
import { ChatHeader } from '../components/chat/ChatHeader'
import { ChatMessageList } from '../components/chat/ChatMessageList'
import { MessageInput } from '../components/chat/MessageInput'
import { MemoryInspector } from '../components/memory/MemoryInspector'
import type { ChatMessage } from '../types/chat'

const PERSONA_NAME = 'Jinne'
const PERSONA_DESCRIPTION = 'Closer, Over Time'

export function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [streamingContent, setStreamingContent] = useState<string | null>(null)
  const [isSending, setIsSending] = useState(false)
  const [memoryRefreshToken, setMemoryRefreshToken] = useState(0)

  async function handleSend(userText: string) {
    const userMessage: ChatMessage = { id: crypto.randomUUID(), role: 'user', content: userText }
    setMessages((prev) => [...prev, userMessage])
    setIsSending(true)
    setStreamingContent('')

    let assembled = ''
    await streamChat(userText, {
      onChunk: (text) => {
        assembled += text
        setStreamingContent(assembled)
      },
      onDone: () => {
        setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: 'assistant', content: assembled }])
        setStreamingContent(null)
        setIsSending(false)
        setMemoryRefreshToken((token) => token + 1)
      },
      onError: (message) => {
        setMessages((prev) => [
          ...prev,
          { id: crypto.randomUUID(), role: 'assistant', content: `(sorry, something went wrong: ${message})` },
        ])
        setStreamingContent(null)
        setIsSending(false)
      },
    })
  }

  return (
    <div className="flex h-screen bg-bg text-text">
      <div className="flex flex-1 flex-col">
        <ChatHeader name={PERSONA_NAME} personaDescription={PERSONA_DESCRIPTION} />
        <ChatMessageList messages={messages} streamingContent={streamingContent} />
        <MessageInput onSend={handleSend} disabled={isSending} />
      </div>
      <MemoryInspector refreshToken={memoryRefreshToken} />
    </div>
  )
}
