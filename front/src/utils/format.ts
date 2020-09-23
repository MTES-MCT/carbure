export function truncate(value: string = "", len: number = 18) {
  return value.length > len ? value.slice(0, len).trim() + "…" : value
}
