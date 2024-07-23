import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"
import { Button, ExternalLink, MailTo } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { AlertTriangle, Plus, Return, Send } from "common/components/icons"
import { usePortal } from "common/components/portal"
import Tag from "common/components/tag"
import { Trans, useTranslation } from "react-i18next"
import { useMatch } from "react-router-dom"
import ApplicationTabs from "../../../double-counting-admin/components/applications/application-tabs"
import FileApplicationInfo from "../../../double-counting-admin/components/files-checker/file-application-info"
import { DoubleCountingFileInfo } from "../../types"
import { SendApplicationAdminDialog } from "../../../double-counting-admin/components/files-checker/send-application-dialog"
import { SendApplicationProducerDialog } from "../send-application-dialog"
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
    <Dialog fullscreen onClose={onClose}>
      <header>
        <Tag big variant="success">
          {t("Valide")}
        </Tag>
        <h1>{t("Dossier double comptage")}</h1>
      </header>

      <main>
        <FileApplicationInfo fileData={fileData} />
        <section>
          {fileData.has_dechets_industriels && <DechetIndustrielAlert />}
        </section>
        <ApplicationTabs
          sourcing={fileData.sourcing}
          production={fileData.production}
        />
      </main>

      <footer>
        <Button
          icon={isProducerMatch ? Send : Plus}
          label={
            isProducerMatch ? t("Envoyer la demande") : t("Ajouter le dossier")
          }
          variant="primary"
          action={showProductionSiteDialog}
        />

        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>
    </Dialog>
  )
}

export default ValidDetailsDialog
