export function normalizeTree<T>(
  tree: T[],
  normalize: Normalizer<T> = defaultNormalizer,
  filter: Filter<T> = defaultFilter
) {
  const normTree = tree.map((item) => {
    const norm = normalize(item)

    const normTree: NormalizedTree<T> = {
      value: item,
      key: norm.key,
      label: norm.label,
      disabled: norm.disabled,
    }

    if (norm.children) {
      normTree.children = normalizeTree(norm.children, normalize, filter)
    }

    return normTree
  })

  return normTree.filter(filter)
}

export function denormalizeTree<T>(tree: NormalizedTree<T>[]) {
  return tree.map((item) => item.value)
}

export function listTreeItems<T>(
  tree: NormalizedTree<T>[]
): NormalizedTree<T>[] {
  return tree.flatMap((item) =>
    item.children
      ? [item, ...listTreeItems(item.children)].filter((item) => !item.disabled)
      : item
  )
}

export interface NormalizedTree<T> extends Normalized<T> {
  children?: NormalizedTree<T>[]
}

export type Filter<T> = (item: NormalizedTree<T>) => boolean
export const defaultFilter = Boolean

export interface Option {
  key: string
  label: string
}

export interface Normalized<T> {
  key: string
  label: string
  value: T
  disabled?: boolean
}

export type Normalizer<T> = (value: T) => {
  key: string
  label: string
  disabled?: boolean
  children?: T[]
}
export const defaultNormalizer: Normalizer<any> = (value) => {
  if (value.key && value.label) {
    return { key: value.key, label: value.label }
  } else {
    return { key: String(value), label: String(value) }
  }
}
