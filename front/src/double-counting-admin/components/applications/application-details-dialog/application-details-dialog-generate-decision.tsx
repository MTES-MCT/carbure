import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"
import { Confirm } from "common/components/dialog"
import { AlertTriangle, Download } from "common/components/icons"
import { Input } from "common/components/input"
import { useNotify } from "common/components/notifications"
import { PortalInstance } from "common/components/portal"
import { hasIndustrialWastes } from "double-counting-admin/utils"
import { DoubleCountingApplicationDetails } from "double-counting/types"
import { useTranslation } from "react-i18next"
import * as api from "../../../api"
import { useState } from "react"

type ApplicationDetailsDialogGenerateDecisionProps = {
  application: DoubleCountingApplicationDetails
  onClose: PortalInstance["close"]
}
const ApplicationDetailsDialogGenerateDecision = ({
  application,
  onClose,
}: ApplicationDetailsDialogGenerateDecisionProps) => {
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
    <Confirm
      variant="primary"
      title={t("Générer la décision double comptage")}
      description={
        <>
          {hasIndustrialWastes(application) && (
            <div style={{ marginBottom: "8px" }}>
              <Alert
                variant="info"
                icon={AlertTriangle}
                style={{ marginBottom: "8px" }}
              >
                <p>
                  {t(
                    "La demande d’agrément du producteur comporte des déchets industriels. Afin de les incorporer dans la décision, veuillez les noter ci-dessous."
                  )}
                </p>
              </Alert>
              <Input
                value={industrialWastes}
                onChange={(e) => setIndustrialWastes(e.target.value)}
                label={t(
                  "Lister ici les déchets industriels - séparés par une virgule :"
                )}
                placeholder={t(
                  "Ex: huile de blanchiment, huile acide contaminée par du souffre"
                )}
                required
              />
            </div>
          )}
          <p>
            {t(
              "Voulez-vous vraiment télécharger la décision double comptage ?"
            )}
          </p>
          <p>
            {t(
              "Une fois la demande d'agrément validée, la décision sera disponible sur la page de l'agrément actif."
            )}
          </p>
        </>
      }
      confirm={t("Générer la décision")}
      icon={Download}
      onClose={onClose}
      onConfirm={() => Promise.resolve(downloadDoubleCountingApplication())}
    />
  )
}

export default ApplicationDetailsDialogGenerateDecision
