import Button from "common/components/button"
import { Upload } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { useTranslation } from "react-i18next"
import DoubleCountingFilesCheckerDialog from "./files-checker-dialog"

const FilesCheckerUploadButton = () => {
  const portal = usePortal()
  const { t } = useTranslation()

  const showAgreementsChecker = () => {
    portal((close) => <DoubleCountingFilesCheckerDialog onClose={close} />)
  }

  return (
    <Button
      asideX
      variant="secondary"
      icon={Upload}
      label={t("Vérifier des dossiers")}
      action={showAgreementsChecker}
    />
  )
}

export default FilesCheckerUploadButton
