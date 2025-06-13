import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog2"
import { Send } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { useTranslation } from "react-i18next"
import FileApplicationInfo from "../files-checker/file-application-info"
import { DoubleCountingFile, DoubleCountingFileInfo } from "../../types"
import { SendApplicationProducerDialog } from "./send-application-dialog"
import ApplicationTabs from "../applications/application-tabs"
import Badge from "@codegouvfr/react-dsfr/Badge"
import { DoubleCountPeriod } from "./double-count-period"
import { useState } from "react"
import { DechetIndustrielAlert } from "./industrial-waste-alert"

export type ValidDetailsDialogProps = {
  file: File
  fileData: DoubleCountingFileInfo
  onClose: () => void
}

export const ValidDetailsDialog = ({
  file,
  fileData,
  onClose,
}: ValidDetailsDialogProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  const [extraFiles, setExtraFiles] = useState<DoubleCountingFile[]>([])

  function showProductionSiteDialog() {
    portal((close) => (
      <SendApplicationProducerDialog
        file={file}
        fileData={fileData}
        extraFiles={extraFiles}
        onSuccess={onClose}
        onClose={close}
      />
    ))
  }

  const isPendingFiles =
    fileData.has_dechets_industriels && extraFiles.length === 0

  return (
    <Dialog
      fullscreen
      onClose={onClose}
      header={
        <>
          <Dialog.Title>
            <Badge severity="success">{t("Valide")}</Badge>
            {t("Dossier double comptage")}
          </Dialog.Title>
          <Dialog.Description>
            <FileApplicationInfo fileData={fileData} />
          </Dialog.Description>
        </>
      }
      footer={
        <Button
          icon={Send}
          label={t("Envoyer la demande")}
          variant="primary"
          action={showProductionSiteDialog}
        />
      }
    >
      <DoubleCountPeriod startYear={fileData.start_year} />
      {isPendingFiles && <DechetIndustrielAlert />}
      <ApplicationTabs
        sourcing={fileData.sourcing}
        production={fileData.production}
        files={extraFiles}
        onAddFiles={(addedFiles) => {
          setExtraFiles([...extraFiles, ...addedFiles])
        }}
        onDeleteFile={(file) => {
          setExtraFiles(
            extraFiles.filter((f) => f.file_name !== file.file_name)
          )
        }}
      />
    </Dialog>
  )
}

export default ValidDetailsDialog
