import { ElecOperationSector } from "accounting/types"
import { CategoryEnum } from "common/types"
import { useTranslation } from "react-i18next"

export const useFormatters = () => {
  const { t } = useTranslation()

  const formatCategory = (category: string) => {
    switch (category) {
      case CategoryEnum.OTHER:
        return t("Autres biocarburants")
      case ElecOperationSector.ELEC:
        return t("Électricité")
    }
    return category
  }

  return { formatCategory }
}
