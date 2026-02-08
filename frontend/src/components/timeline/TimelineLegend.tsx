const items = [
  { color: 'bg-green-500', label: 'Выполнено' },
  { color: 'bg-yellow-500', label: 'В процессе' },
  { color: 'bg-red-500', label: 'Просрочено' },
  { color: 'bg-gray-400', label: 'Не начато' },
  { color: 'bg-purple-500', label: 'Экзамен', variant: 'diamond' as const },
] as const

export function TimelineLegend() {
  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
      {items.map((item) => (
        <div key={item.label} className="flex items-center gap-1.5">
          <span
            className={`inline-block w-2.5 h-2.5 ${item.color} ${
              'variant' in item && item.variant === 'diamond' ? 'rotate-45' : 'rounded-full'
            }`}
          />
          <span>{item.label}</span>
        </div>
      ))}
    </div>
  )
}
