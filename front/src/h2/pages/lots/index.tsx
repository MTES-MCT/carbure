import { useTranslation } from "react-i18next"

import { ActionsPage } from "traceability/components/actions-page"
import { ActionIndustry } from "traceability/types"

const LotsPage = () => {
  const { t } = useTranslation()

  return (
    <ActionsPage
      title={t("Lots")}
      yearsRoot="lots"
      fixedQuery={{ industry: ActionIndustry.H2 }}
      labels={{ material: t("Nature d'H2") }}
      queryKey="h2-lots"
    />
  )
}

export default LotsPage
