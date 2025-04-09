import { formatSector } from "accounting/utils/formatters"

export const useNormalizeSector = () => {
  const normalizeSector = (sector: string) => ({
    label: formatSector(sector),
    value: sector,
  })

  return normalizeSector
}
