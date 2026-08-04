import { formatNumber } from "common/utils/formatters"
import { useState } from "react"

type MacInputProps = {
  value: number | undefined
  onChange: (value: number | undefined) => void
}
export const MacInput = ({ value, onChange }: MacInputProps) => {
  const [focused, setFocused] = useState(false)

  return (
    <input
      min={0}
      value={
        focused ? (value ?? "") : value !== undefined ? formatNumber(value) : ""
      }
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      onChange={(e) => onChange(parseFloat(e.target.value))}
    />
  )
}
