import { describe, expect, it, vi } from "vitest"
import { act, renderHook } from "@testing-library/react"
import i18n from "i18n"
import { useGroupedNumberInput } from "./use-grouped-number-input"

describe("useGroupedNumberInput", () => {
  it("formats display value with grouped thousands", () => {
    const initialLanguage = i18n.language
    i18n.language = "fr-FR"

    const { result } = renderHook(() => useGroupedNumberInput({ value: 12345 }))

    expect(result.current.displayValue).toMatch(/12[\s\u00A0\u202F]345/)

    i18n.language = initialLanguage
  })

  it("parses grouped values and emits a number", () => {
    const onChange = vi.fn()
    const { result } = renderHook(() =>
      useGroupedNumberInput({
        value: undefined,
        onChange,
      })
    )
    act(() => result.current.handleChange?.("12 345"))

    expect(onChange).toHaveBeenCalledWith(12345)
  })

  it("parses decimal values with comma separator", () => {
    const onChange = vi.fn()
    const { result } = renderHook(() =>
      useGroupedNumberInput({
        value: undefined,
        onChange,
      })
    )
    act(() => result.current.handleChange?.("12,5"))

    expect(onChange).toHaveBeenCalledWith(12.5)
  })

  it("does not emit on trailing decimal separator", () => {
    const onChange = vi.fn()
    const { result } = renderHook(() =>
      useGroupedNumberInput({
        value: undefined,
        onChange,
      })
    )
    act(() => result.current.handleChange?.("12,"))

    expect(onChange).not.toHaveBeenCalled()
  })

  it("rejects non numeric characters", () => {
    const onChange = vi.fn()
    const { result } = renderHook(() =>
      useGroupedNumberInput({
        value: undefined,
        onChange,
      })
    )
    act(() => result.current.handleChange?.("12a"))

    expect(onChange).not.toHaveBeenCalled()
    expect(result.current.displayValue).toBe("")
  })

  it("emits integer on blur after trailing separator", () => {
    const onChange = vi.fn()
    const { result } = renderHook(() =>
      useGroupedNumberInput({
        value: undefined,
        onChange,
      })
    )
    act(() => result.current.handleChange?.("12,"))
    act(() => result.current.handleBlur?.())

    expect(onChange).toHaveBeenCalledWith(12)
  })

  it("emits undefined for empty input", () => {
    const onChange = vi.fn()
    const { result } = renderHook(() =>
      useGroupedNumberInput({
        value: undefined,
        onChange,
      })
    )
    act(() => result.current.handleChange?.(""))

    expect(onChange).toHaveBeenCalledWith(undefined)
  })
})
