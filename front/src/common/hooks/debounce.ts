import { useRef, useState } from "react"

export const useDebounce = <T extends string | number | undefined>({
  value,
  delay,
  onChange,
}: {
  value: T
  delay: number
  onChange: (value?: T) => void
}) => {
  const timeoutRef = useRef<number>()
  const [search, setSearch] = useState<T | undefined>(value)

  function debouncedSearch(search?: T) {
    setSearch(search)
    if (!delay) return onChange?.(search)

    if (timeoutRef.current) window.clearTimeout(timeoutRef.current)
    timeoutRef.current = window.setTimeout(() => onChange?.(search), delay)
  }

  return [search, debouncedSearch] as const
}
