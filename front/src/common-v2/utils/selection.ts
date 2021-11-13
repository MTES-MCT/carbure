export function singleSelection<V>(
  selectedValue: V | undefined,
  onSelectValue: ((value: V | undefined) => void) | undefined
) {
  function isSelected(value: V) {
    if (selectedValue === undefined) return false
    return selectedValue === value
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
    else return selectedValues.includes(value)
  }

  function isAllSelected(values: V[]) {
    const compareValues = (a: V, b: V) => (a < b ? -1 : 1)

    const sortedValues = values.sort(compareValues)
    const sortedSelection = (selectedValues ?? []).sort(compareValues)

    return (
      sortedValues.length === sortedSelection.length &&
      sortedValues.every((key, i) => key === sortedSelection[i])
    )
  }

  function onSelect(value: V | undefined) {
    if (value === undefined) return onSelectValues?.([])

    const values = selectedValues ?? []
    const selected = isSelected(value)
      ? // remove item from selection
        values.filter((v) => v !== value)
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
