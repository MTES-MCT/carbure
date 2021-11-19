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
