import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog2"
import { Plus, Send } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { useTranslation } from "react-i18next"
import { useMatch } from "react-router-dom"
import FileApplicationInfo from "../../../double-counting-admin/components/files-checker/file-application-info"
import { DoubleCountingFileInfo } from "../../types"
import { SendApplicationAdminDialog } from "../../../double-counting-admin/components/files-checker/send-application-dialog"
import { SendApplicationProducerDialog } from "../send-application-dialog"
import { DechetIndustrielAlert } from "./industrial-waste-alert"
import ApplicationTabs from "../applications/application-tabs"
import Badge from "@codegouvfr/react-dsfr/Badge"

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
  const isProducerMatch = useMatch("/org/:entity/settings*")

  function showProductionSiteDialog() {
    if (isProducerMatch) {
      portal((close) => (
        <SendApplicationProducerDialog
          fileData={fileData}
          onClose={() => {
            close()
            onClose()
          }}
          file={file}
        />
      ))
    } else {
      portal((close) => (
        <SendApplicationAdminDialog
          fileData={fileData}
          onClose={() => {
            close()
            onClose()
          }}
          file={file}
        />
      ))
    }
  }

  return (
    <Dialog
      fullscreen
      onClose={onClose}
      header={
        <Dialog.Title>
          <Badge severity="success">{t("Valide")}</Badge>
          {t("Dossier double comptage")}
        </Dialog.Title>
      }
      footer={
        <Button
          icon={isProducerMatch ? Send : Plus}
          label={
            isProducerMatch ? t("Envoyer la demande") : t("Ajouter le dossier")
          }
          variant="primary"
          action={showProductionSiteDialog}
        />
      }
    >
      <FileApplicationInfo fileData={fileData} />

      {fileData.has_dechets_industriels && <DechetIndustrielAlert />}

      <ApplicationTabs
        sourcing={fileData.sourcing}
        production={fileData.production}
      />
    </Dialog>
  )
}

export default ValidDetailsDialog
