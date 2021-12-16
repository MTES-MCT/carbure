export function singleSelection<V>(
  selectedValue: V | undefined,
  onSelectValue: ((value: V | undefined) => void) | undefined
) {
  const selectedKey = JSON.stringify(selectedValue)

  function isSelected(value: V) {
    if (selectedValue === undefined) return false
    return selectedKey === JSON.stringify(value)
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
  const selectedKeys = selectedValues?.map((value) => JSON.stringify(value))

  function isSelected(value: V | undefined) {
    if (selectedKeys === undefined || value === undefined) return false
    else return selectedKeys.includes(JSON.stringify(value))
  }

  function isAllSelected(values: V[]) {
    if (!selectedKeys) return false

    const keys = values.map((value) => JSON.stringify(value))
    const sortedKeys = keys.sort()
    const sortedSelection = selectedKeys.sort()

    return (
      sortedKeys.length === sortedSelection.length &&
      sortedKeys.every((key, i) => key === sortedSelection[i])
    )
  }

  function onSelect(value: V | undefined) {
    if (value === undefined) return onSelectValues?.([])

    const key = JSON.stringify(value)
    const values = selectedValues ?? []
    const selected = isSelected(value)
      ? // remove item from selection
        values.filter((v) => JSON.stringify(v) !== key)
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
