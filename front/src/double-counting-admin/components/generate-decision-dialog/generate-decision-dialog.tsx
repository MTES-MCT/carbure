import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"
import Dialog from "common/components/dialog"
import { AlertTriangle, Download, Return } from "common/components/icons"
import { Input } from "common/components/input"
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
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Générer la décision double comptage")}</h1>
      </header>

      <main>
        <section>
          <Form
            id="generate-decision"
            onSubmit={downloadDoubleCountingApplication}
          >
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
          </Form>
        </section>
      </main>

      <footer>
        <Button
          variant="primary"
          icon={Download}
          label={t("Générer la décision")}
          submit="generate-decision"
        />
        <Button asideX icon={Return} action={onClose} label={t("Retour")} />
      </footer>
    </Dialog>
  )
}

export default GenerateDecisionDialog
