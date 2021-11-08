import { defaultNormalizer, Normalizer } from "./normalize";

export function singleSelection<T>(
  selectedItem: T | undefined,
  onSelectItem: ((item: T | undefined) => void) | undefined,
  normalize: Normalizer<T>
) {
  function isSelected(item: T) {
    if (!selectedItem) return false;
    return normalize(selectedItem).key === normalize(item).key;
  }

  function onSelect(item: T | undefined) {
    onSelectItem?.(item);
  }

  return { isSelected, onSelect };
}

export function multipleSelection<T>(
  selectedItems: T[] | undefined,
  onSelectItems: ((items: T[]) => void) | undefined,
  normalize: Normalizer<T> = defaultNormalizer
) {
  function isSelected(item: T | undefined) {
    if (!selectedItems || !item) return false;

    const { key } = normalize(item);
    return selectedItems
      .map(normalize)
      .map((n) => n.key)
      .includes(key);
  }

  function isAllSelected(items: T[]) {
    const sortedItems = items
      .map(normalize)
      .sort((a, b) => (a.key < b.key ? -1 : 1));

    const sortedSelection = (selectedItems ?? [])
      .map(normalize)
      .sort((a, b) => (a.key < b.key ? -1 : 1));

    return (
      sortedItems.length === sortedSelection.length &&
      sortedItems.every((item, i) => item.key === sortedSelection[i].key)
    );
  }

  function onSelect(item: T | undefined) {
    if (!item) return onSelectItems?.([]);

    const { key } = normalize(item);
    const items = selectedItems ?? [];

    const selected = isSelected(item)
      ? // remove item from selection
        items.filter((i) => normalize(i).key !== key)
      : // or add it at the end
        [...items, item];

    onSelectItems?.(selected);
  }

  function onSelectAll(items: T[]) {
    if (isAllSelected(items)) {
      onSelectItems?.([]);
    } else {
      onSelectItems?.(items);
    }
  }

  return { isSelected, isAllSelected, onSelect, onSelectAll };
}
