import { formatSector } from "accounting/utils/formatters"
import { useTranslation } from "react-i18next"

export const useNormalizeSector = () => {
  const { t } = useTranslation()

  const normalizeSector = (sector: string) => ({
    label: t(formatSector(sector)),
    value: sector,
  })

  return normalizeSector
}
