import { Button } from "common/components/button2"
import { usePortal } from "common/components/portal"
import { useTranslation } from "react-i18next"
import DoubleCountingFilesCheckerDialog from "./files-checker-dialog"

const FilesCheckerUploadButton = ({ label }: { label?: string }) => {
  const portal = usePortal()
  const { t } = useTranslation()

  const showApplicationsChecker = () => {
    portal((close) => <DoubleCountingFilesCheckerDialog onClose={close} />)
  }

  return (
    <Button asideX iconId="ri-upload-line" onClick={showApplicationsChecker}>
      {label || t("Ajouter des demandes d'agrément")}
    </Button>
  )
}

export default FilesCheckerUploadButton
