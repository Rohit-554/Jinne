interface ChatHeaderProps {
  name: string
  personaDescription: string
}

export function ChatHeader({ name, personaDescription }: ChatHeaderProps) {
  return (
    <div className="border-b border-border px-6 py-4">
      <h1 className="text-lg font-semibold text-text">{name}</h1>
      <p className="text-sm text-text-secondary">{personaDescription}</p>
    </div>
  )
}
