export function normalizeItems<T, V>(
  tree: T[] = [],
  normalize: Normalizer<T, V> = defaultNormalizer,
  filter: Filter<T, V> = defaultFilter
) {
  const normalizeItem = (data: T) => {
    const { children, ...norm } = normalize(data)
    const normTree: Normalized<T, V> = { data, ...norm }
    if (children) normTree.children = normalizeItems(children, normalize, filter) // prettier-ignore
    return normTree
  }

  return tree.map(normalizeItem).filter(filter)
}

export function denormalizeItems<T, V>(tree: Normalized<T, V>[]) {
  return tree.map((item) => item.data)
}

export function listTreeItems<T, V>(
  tree: Normalized<T, V>[]
): Normalized<T, V>[] {
  return tree.flatMap((item) =>
    item.children
      ? [item, ...listTreeItems(item.children)].filter((item) => !item.disabled)
      : item
  )
}

export function labelize<T, V>(
  items: T[] = [],
  normalize: Normalizer<T, V>,
  join: string = ", "
) {
  return items.map((item) => normalize(item).label).join(join)
}

export type Filter<T, V> = (item: Normalized<T, V>) => boolean
export const defaultFilter = Boolean

export interface Normalized<T, V> {
  data: T
  value: V
  label: string
  disabled?: boolean
  children?: Normalized<T, V>[]
}

export interface Option<V = string> {
  value: V
  label: string
}

export type Normalizer<T, V = string> = (item: T) => {
  value: V
  label: string
  disabled?: boolean
  children?: T[]
}
export const defaultNormalizer: Normalizer<any, any> = (item) => {
  if (item instanceof Object && "value" in item && "label" in item) {
    return { value: item.value, label: item.label }
  } else {
    return { value: item, label: String(item) }
  }
}
