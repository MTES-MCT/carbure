import { useTranslation } from "react-i18next"
import Button from "common-v2/components/button"
import { Certificate } from "common-v2/components/icons"

export const DeclarationButton = () => {
  const { t } = useTranslation()
  return (
    <Button
      asideX
      variant="primary"
      icon={Certificate}
      label={t("Valider ma déclaration")}
    />
  )
}
