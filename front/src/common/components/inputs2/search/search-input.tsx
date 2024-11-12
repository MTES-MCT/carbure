import SearchBar from "@codegouvfr/react-dsfr/SearchBar"
import { useEffect, useRef, useState } from "react"

type SearchInputProps = {
  debounce?: number
  onChange?: (search: string) => void
  value?: string
  placeholder?: string
  className?: string
}
export const SearchInput = ({
  debounce,
  onChange,
  value,
  placeholder,
  ...props
}: SearchInputProps) => {
  const timeoutRef = useRef<number>()
  const [search, setSearch] = useState(value ?? "")

  useEffect(() => {
    setSearch(value ?? "")
  }, [value])

  function debouncedSearch(search: string) {
    setSearch(search)
    if (!debounce) return onChange?.(search)

    if (timeoutRef.current) window.clearTimeout(timeoutRef.current)
    timeoutRef.current = window.setTimeout(() => onChange?.(search), debounce)
  }
  return (
    <SearchBar
      renderInput={(props) => (
        <input
          {...props}
          value={search ?? ""}
          onChange={(e) => debouncedSearch(e.target.value)}
        />
      )}
      label={placeholder}
      {...props}
    />
  )
}
