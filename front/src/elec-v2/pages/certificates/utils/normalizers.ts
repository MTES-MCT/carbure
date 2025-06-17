import { getSourceLabel } from "./formatters"

export function normalizeSource(source: string) {
  return {
    value: source,
    label: getSourceLabel(source),
  }
}
