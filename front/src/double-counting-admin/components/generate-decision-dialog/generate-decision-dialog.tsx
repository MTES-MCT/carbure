import useEntity from "common/hooks/entity"
import { Notice } from "common/components/notice"
import { Dialog } from "common/components/dialog2"
import { Download } from "common/components/icons"
import { TextInput } from "common/components/inputs2"
import { useNotify } from "common/components/notifications"
import { PortalInstance } from "common/components/portal"
import { hasIndustrialWastes } from "double-counting-admin/utils"
import { DoubleCountingApplicationDetails } from "double-counting/types"
import { useTranslation } from "react-i18next"
import * as api from "../../api"
import { useState } from "react"
import Form from "common/components/form"
import Button from "common/components/button"

type GenerateDecisionDialogProps = {
  application: DoubleCountingApplicationDetails
  onClose: PortalInstance["close"]
}
const GenerateDecisionDialog = ({
  application,
  onClose,
}: GenerateDecisionDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const entity = useEntity()
  const [industrialWastes, setIndustrialWastes] = useState("")

  const downloadDoubleCountingApplication = () => {
    api.downloadDoubleCountingApplication(
      entity.id,
      application.id,
      industrialWastes
    )

    notify(t("La décision a bien été générée."), { variant: "success" })
    onClose()
  }
  return (
    <Dialog
      onClose={onClose}
      header={
        <Dialog.Title>{t("Générer la décision double comptage")}</Dialog.Title>
      }
      footer={
        <Button
          variant="primary"
          icon={Download}
          label={t("Générer la décision")}
          submit="generate-decision"
        />
      }
    >
      <Form id="generate-decision" onSubmit={downloadDoubleCountingApplication}>
        {hasIndustrialWastes(application) && (
          <>
            <Notice variant="info" icon="ri-alert-line">
              {t(
                "La demande d’agrément du producteur comporte des déchets industriels. Afin de les incorporer dans la décision, veuillez les noter ci-dessous."
              )}
            </Notice>

            <TextInput
              value={industrialWastes}
              onChange={(v) => setIndustrialWastes(v ?? "")}
              label={t(
                "Lister ici les déchets industriels - séparés par une virgule :"
              )}
              placeholder={t(
                "Ex: huile de blanchiment, huile acide contaminée par du souffre"
              )}
              required
            />
          </>
        )}
      </Form>
      <p>
        {t("Voulez-vous vraiment télécharger la décision double comptage ?")}
      </p>
    </Dialog>
  )
}

export default GenerateDecisionDialog
