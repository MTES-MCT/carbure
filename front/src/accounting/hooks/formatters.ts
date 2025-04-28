import { CategoryEnum } from "common/types"
import { useTranslation } from "react-i18next"

export const useFormatters = () => {
  const { t } = useTranslation()

  const formatCategory = (category: CategoryEnum) => {
    switch (category) {
      case CategoryEnum.OTHER:
        return t("Autres biocarburants")
    }
    return category
  }

  return { formatCategory }
}
