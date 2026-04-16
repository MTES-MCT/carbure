import { Button } from "common/components/button2"
import { useTranslation } from "react-i18next"
import { downloadAnnualDeclaration } from "biomethane/api"
import useEntity from "common/hooks/entity"

interface DownloadDeclarationButtonProps {
  year: number
  producerId?: number
}

export const DownloadDeclarationButton = ({
  year,
  producerId,
}: DownloadDeclarationButtonProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  return (
    <Button
      iconId="ri-download-line"
      priority="secondary"
      onClick={() => downloadAnnualDeclaration(entity.id, year, producerId)}
    >
      {t("Télécharger la déclaration")}
    </Button>
  )
}
