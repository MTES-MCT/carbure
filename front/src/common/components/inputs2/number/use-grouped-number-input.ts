import i18n from "i18n"
import { useEffect, useMemo, useState } from "react"

type UseGroupedNumberInputParams = {
  value?: number | null
  onChange?: (value: number | undefined) => void
}

const stripGrouping = (raw: string) => raw.replaceAll(/[\s\u00A0\u202F]/g, "")

const normalizeDecimalSeparator = (raw: string) => raw.replace(",", ".")
const isAllowedRawInput = (raw: string) => /^-?[\d\s\u00A0\u202F,.]*$/.test(raw)

const toNormalizedRaw = (raw: string) =>
  normalizeDecimalSeparator(stripGrouping(raw))

const countDecimalSeparators = (raw: string) =>
  (raw.match(/[,.]/g) || []).length

const hasTrailingDecimalSeparator = (raw: string) => /[,.]$/.test(raw)

const parseNormalized = (raw: string) => {
  const parsed = Number.parseFloat(raw)
  return Number.isNaN(parsed) ? undefined : parsed
}

const formatGrouped = (value: number, locale: string) =>
  Number.isFinite(value)
    ? new Intl.NumberFormat(locale, { maximumFractionDigits: 20 }).format(value)
    : ""

export const useGroupedNumberInput = ({
  value,
  onChange,
}: UseGroupedNumberInputParams) => {
  const locale = i18n.language || "fr-FR"
  const externalDisplayValue = useMemo(
    () =>
      value === null || value === undefined ? "" : formatGrouped(value, locale),
    [locale, value]
  )
  const [displayValue, setDisplayValue] = useState(externalDisplayValue)

  useEffect(() => {
    setDisplayValue(externalDisplayValue)
  }, [externalDisplayValue])

  const emitAndFormat = (parsed: number) => {
    onChange?.(parsed)
    setDisplayValue(formatGrouped(parsed, locale))
  }

  const handleChange = onChange
    ? (raw: string) => {
        if (!isAllowedRawInput(raw)) {
          return
        }

        if (countDecimalSeparators(raw) > 1) {
          return
        }

        setDisplayValue(raw)

        const normalized = toNormalizedRaw(raw)
        if (!normalized) {
          onChange(undefined)
          return
        }

        // Keep transient state like "12," without emitting.
        if (hasTrailingDecimalSeparator(raw)) {
          return
        }

        const parsed = parseNormalized(normalized)
        if (parsed === undefined) {
          onChange(undefined)
          return
        }

        emitAndFormat(parsed)
      }
    : undefined

  const handleBlur = onChange
    ? () => {
        const normalized = toNormalizedRaw(displayValue)
        if (!normalized) {
          setDisplayValue("")
          onChange(undefined)
          return
        }

        // Finalize "12," as 12 when leaving the field.
        const parsed = parseNormalized(normalized)
        if (parsed === undefined) {
          return
        }

        emitAndFormat(parsed)
      }
    : undefined

  return {
    displayValue,
    handleChange,
    handleBlur,
  }
}
