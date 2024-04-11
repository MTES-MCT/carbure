import { standardize } from "./formatters"

export function uniqueBy<T, V>(list: T[], by: (value: T) => V) {
  const keys = list.map(by)
  return list.filter((item, i) => keys.lastIndexOf(by(item)) === i)
}

export function sortBy<T, V>(list: T[], by: (value: T) => V) {
  return list.sort((a, b) => {
    const byA = by(a)
    const byB = by(b)

    if (typeof byA === "number" && typeof byB === "number") {
      return byA - byB
    } else {
      return String(by(a)).localeCompare(String(by(b)), "fr")
    }
  })
}

export function groupBy<T>(list: T[], by: (value: T) => string | number) {
  const groups: Record<string, T[]> = {}
  list.forEach((item) => {
    const group = by(item)
    groups[group] = groups[group] || []
    groups[group].push(item)
  })
  return groups
}

export function compact<T>(list: Array<T | false | null | undefined>) {
  return list.filter(
    (item) => item !== false && item !== null && item !== undefined
  ) as Array<T>
}

export function isUndefined(value: unknown) {
  return value === undefined || value === null
}

export function isScalar(value: unknown) {
  return (
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean" ||
    value === undefined ||
    value === null
  )
}

export function matchesSearch(
  search: string,
  fields: string[],
  exact?: boolean
) {
  const stdQuery = standardize(search)
  return fields.some((field) => {
    const stdField = standardize(field)
    return exact ? stdField === stdQuery : stdField.includes(stdQuery)
  })
}

export function matches(source: any, target: any, strict = false): boolean {
  // consider that null and undefined are actually equivalent
  if (isUndefined(source) && isUndefined(target)) {
    return true
  }

  if (isScalar(source) || isScalar(target)) {
    return source === target
  }

  for (const key in source) {
    if (!(key in target)) {
      if (strict) return false
      else continue
    }

    if (!matches(source[key], target[key])) {
      return false
    }
  }

  return true
}
