import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { Plus, Return } from "common/components/icons"
import { usePortal } from "common/components/portal"
import Tag from "common/components/tag"
import { useTranslation } from "react-i18next"
import { useMatch } from "react-router-dom"
import FileApplicationInfo from "../../../double-counting/components/files-checker/file-application-info"
import { DoubleCountingFileInfo } from "../../../double-counting/types"
import { ElecChargingPointsApplicationCheckInfo } from "elec/types"
import { addChargingPointsApplication } from "settings/api/elec"
import { useMutation } from "common/hooks/async"

export type ValidDetailsDialogProps = {
  fileData: ElecChargingPointsApplicationCheckInfo
  onClose: () => void
}

export const ValidDetailsDialog = ({
  fileData,
  onClose,
}: ValidDetailsDialogProps) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const isProducerMatch = useMatch("/org/:entity/settings*")

  const addApplication = useMutation(addChargingPointsApplication, {
    invalidates: ["dc-applications", "dc-snapshot"],
    onSuccess() {
      onClose()
      // notify(t("Le dossier a été ajouté !"), { variant: "success" })
      // navigate({
      //   pathname: '/org/9/double-counting',
      // })
    },
    onError(err) {
      // const errorCode = (err as AxiosError<{ error: string }>).response?.data.error
      // if (errorCode === 'APPLICATION_ALREADY_EXISTS') {
      //   portal((close) => <ReplaceApplicationDialog onReplace={saveApplication} onClose={close} />)
      // } 
      // else {
      //   notifyError(err, t("Impossible d'ajouter le dossier"))
      // }
    },
  })

  return (
    <Dialog fullscreen onClose={onClose}>
      <header>
        <Tag big variant="success">
          {t("Valide")}
        </Tag>
        <h1>{t("Inscription des points de recharge")}</h1>
      </header>

      <main>

        <section>
          <p style={{ textAlign: 'left' }}>
            {t("Votre fichier {{fileName}}, ne comporte aucune erreur.", { fileName: fileData.file_name })}
          </p>
          <p>
            Les 90 points de recharge ont été importés dans votre espace CarbuRe.
            Un échantillon de points de recharge vous sera transmis directement par e-mail de notre part dans le but de réaliser un audit.
          </p>
        </section>
      </main>

      <footer>
        <Button
          icon={Plus}
          label={t("Envoyer la demande d'inscription")}
          variant="primary"
          action={() => { }}
        />

        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>

    </Dialog>
  )
}




export default ValidDetailsDialog


