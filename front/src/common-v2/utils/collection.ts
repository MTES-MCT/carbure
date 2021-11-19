export function uniqueBy<T, V>(list: T[], by: (value: T) => V) {
  const keys = list.map(by)
  return list.filter((item, i) => keys.lastIndexOf(by(item)) === i)
}

export function sortBy<T, V>(list: T[], by: (value: T) => V) {
  return list.sort((a, b) => String(by(a)).localeCompare(String(by(b)), "fr"))
}
