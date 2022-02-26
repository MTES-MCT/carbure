import { matches } from "./collection"

export function singleSelection<V>(
  selectedValue: V | undefined,
  onSelectValue: ((value: V | undefined) => void) | undefined
) {
  function isSelected(value: V) {
    if (selectedValue === undefined) return false
    return matches(value, selectedValue)
  }

  function onSelect(value: V | undefined) {
    onSelectValue?.(value)
  }

  return { isSelected, onSelect }
}

export function multipleSelection<V>(
  selectedValues: V[] | undefined,
  onSelectValues: ((value: V[]) => void) | undefined
) {
  function isSelected(value: V | undefined) {
    if (selectedValues === undefined || value === undefined) return false
    else return selectedValues.some((v) => matches(v, value))
  }

  function isAllSelected(values: V[]) {
    if (!selectedValues) return false
    return values.every(isSelected)
  }

  function onSelect(value: V | undefined) {
    if (value === undefined) return onSelectValues?.([])

    const values = selectedValues ?? []
    const selected = isSelected(value)
      ? // remove item from selection
        values.filter((v) => !matches(v, value))
      : // or add it at the end
        [...values, value]

    onSelectValues?.(selected)
  }

  function onSelectAll(values: V[]) {
    if (isAllSelected(values)) {
      onSelectValues?.([])
    } else {
      onSelectValues?.(values)
    }
  }

  return { isSelected, isAllSelected, onSelect, onSelectAll }
}
