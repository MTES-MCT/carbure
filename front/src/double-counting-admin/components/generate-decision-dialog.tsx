/**
 * Dialog to generate a decision for an agreement or an application
 */
import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"
import { Confirm } from "common/components/dialog"
import { AlertTriangle, Download } from "common/components/icons"
import { Input } from "common/components/input"
import { useNotify } from "common/components/notifications"
import { PortalInstance } from "common/components/portal"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import * as api from "../api"
import { useState } from "react"

type GenerateDecisionDialogProps = {
  applicationOrAgreementId: number
  hasIndustrialWastes: boolean
  onClose: PortalInstance["close"]
  // onChangeIndustrialWastes: (value: string) => void
  // industrialWastes: string
}
const ApplicationDetailsDialogGenerateDecision = ({
  applicationOrAgreementId,
  hasIndustrialWastes,
  onClose,
}: GenerateDecisionDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()
  const entity = useEntity()
  const [industrialWastes, setIndustrialWastes] = useState("")

  const downloadDoubleCountingApplication = () => {
    api.downloadDoubleCountingApplication(
      entity.id,
      applicationOrAgreementId,
      industrialWastes
    )

    setIndustrialWastes("")
    notify(t("La décision a bien été générée."), { variant: "success" })
    navigate("/org/9/double-counting/agreements")
  }

  return (
    <Confirm
      variant="primary"
      title={t("Accepter la demande d'agrément")}
      description={
        <>
          {hasIndustrialWastes && (
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
              />
            </div>
          )}
          <p>
            {t(
              "Voulez-vous vraiment accepter cette demande d'agrément double comptage ?"
            )}
          </p>
          <p>
            {t(
              "Une fois accepté, vous retrouverez l'agrément correspondant dans la liste des agréments actifs."
            )}
          </p>
          <p>{t("La décision sera directement téléchargée au format word.")}</p>
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
