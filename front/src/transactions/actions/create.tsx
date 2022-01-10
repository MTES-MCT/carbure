import { useTranslation } from "react-i18next"
import Button from "common-v2/components/button"
import { Plus } from "common-v2/components/icons"

export const CreateButton = () => {
  const { t } = useTranslation()
  return (
    <Button
      variant="primary"
      icon={Plus}
      label={t("Créer un lot")}
      to="drafts/add"
    />
  )
}
