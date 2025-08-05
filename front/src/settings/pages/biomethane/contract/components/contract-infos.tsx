import { EditableCard } from "common/molecules/editable-card"
import { useTranslation } from "react-i18next"

export const ContractInfos = () => {
  const { t } = useTranslation()

  return (
    <EditableCard
      title={t("Caractéristiques du contrat d’achat à tarif réglementé")}
      headerActions={null}
    >
      test
    </EditableCard>
  )
}
