export function truncate(value: string = "", len: number) {
  return value.length > len ? value.slice(0, len).trim() + "…" : value
}
