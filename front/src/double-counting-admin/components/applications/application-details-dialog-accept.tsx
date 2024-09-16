import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"
import { Confirm } from "common/components/dialog"
import { AlertTriangle, Download } from "common/components/icons"
import { Input } from "common/components/input"
import { useNotify } from "common/components/notifications"
import { PortalInstance } from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { hasIndustrialWastes } from "double-counting-admin/utils"
import { DoubleCountingApplicationDetails } from "double-counting/types"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import * as api from "../../api"

type ApplicationDetailsDialogAcceptProps = {
  application: DoubleCountingApplicationDetails
  onClose: PortalInstance["close"]
  onChangeIndustrialWastes: (value: string) => void
  industrialWastes: string
}
const ApplicationDetailsDialogAccept = ({
  application,
  onClose,
  onChangeIndustrialWastes,
  industrialWastes,
}: ApplicationDetailsDialogAcceptProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()
  const entity = useEntity()
  const approveApplication = useMutation(api.approveDoubleCountingApplication, {
    invalidates: ["dc-applications", "dc-snapshot", "dc-agreements"],
    onSuccess: () => {
      api.downloadDoubleCountingApplication(
        entity.id,
        application.id,
        industrialWastes
      )
      notify(t("La décision a bien été générée."), { variant: "success" })
      onChangeIndustrialWastes("")
      navigate("/org/9/double-counting/agreements")
    },
  })

  return (
    <Confirm
      variant="primary"
      title={t("Accepter la demande d'agrément")}
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
                onChange={(e) => onChangeIndustrialWastes(e.target.value)}
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
      onConfirm={async () => {
        if (application) {
          await approveApplication.execute(entity.id, application.id)
        }
      }}
    />
  )
}

export default ApplicationDetailsDialogAccept
