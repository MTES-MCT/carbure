import Button from "common/components/button"
import { Upload } from "common/components/icons"
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
    <Button
      asideX
      variant="secondary"
      icon={Upload}
      label={label || t("Ajouter des demandes d'agrément")}
      action={showApplicationsChecker}
    />
  )
}

export default FilesCheckerUploadButton
