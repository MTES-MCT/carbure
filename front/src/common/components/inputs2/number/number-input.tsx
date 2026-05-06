import { Input, InputProps } from "../input"
import { useGroupedNumberInput } from "./use-grouped-number-input"

export type NumberInputProps = InputProps & {
  min?: number
  max?: number
  step?: number
  value?: number | null
  onChange?: (value: number | undefined) => void

  /**
   * Display a formatted value with thousands separators while keeping `onChange`
   * numeric. Uses the current i18n locale.
   */
  groupThousands?: boolean
}

export const NumberInput = ({
  value,
  onChange,
  min,
  max,
  step,
  groupThousands,
  onBlur,
  ...props
}: NumberInputProps) => {
  const { displayValue, handleChange, handleBlur } = useGroupedNumberInput({
    value,
    onChange,
  })

  return (
    <Input
      {...props}
      type={props.readOnly || groupThousands ? "text" : "number"}
      nativeInputProps={{
        min,
        max,
        step,
        inputMode: groupThousands ? "decimal" : undefined,
        value: groupThousands ? displayValue : (value ?? ""),
        onChange: onChange
          ? (e) => {
              if (!groupThousands) {
                const parsed = Number.parseFloat(e.target.value)
                const change = Number.isNaN(parsed) ? undefined : parsed
                onChange(change)
                return
              }
              handleChange?.(e.target.value)
            }
          : undefined,
      }}
      onBlur={
        groupThousands
          ? (event) => {
              handleBlur?.()
              onBlur?.(event)
            }
          : onBlur
      }
    />
  )
}
