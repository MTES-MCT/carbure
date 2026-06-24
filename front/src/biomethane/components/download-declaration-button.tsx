import { Button } from "common/components/button2"
import { useTranslation } from "react-i18next"
import { downloadAnnualDeclaration } from "biomethane/api"
import useEntity from "common/hooks/entity"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { AnnualDeclarationStatus } from "biomethane/types"

interface DownloadDeclarationButtonProps {
  year: number
}

export const DownloadDeclarationButton = ({
  year,
}: DownloadDeclarationButtonProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { annualDeclaration } = useAnnualDeclaration()

  if (annualDeclaration?.status !== AnnualDeclarationStatus.DECLARED) {
    return null
  }

  const handleDownload = () => downloadAnnualDeclaration(entity.id, year)

  return (
    <Button
      iconId="ri-download-line"
      priority="secondary"
      onClick={handleDownload}
    >
      {t("Télécharger la déclaration")}
    </Button>
  )
}
