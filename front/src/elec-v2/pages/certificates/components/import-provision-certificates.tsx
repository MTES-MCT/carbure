import { Button } from "common/components/button2"
import { useTranslation } from "react-i18next"

export const ImportProvisionCertificates = () => {
  const { t } = useTranslation()

  return (
    <Button iconId="fr-icon-draft-fill" asideX>
      {t("Émettre des certificats de fourniture")}
    </Button>
  )
}
