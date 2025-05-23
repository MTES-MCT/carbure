import useEntity from "common/hooks/entity"
import Alert from "common/components/alert"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { AlertCircle, Plus } from "common/components/icons"
import Portal from "common/components/portal"
import { Trans, useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"

interface CompanyInfoMissingSirenDialogProps {
  onClose: () => void
}

export const CompanyInfoMissingSirenDialog = ({
  onClose,
}: CompanyInfoMissingSirenDialogProps) => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const entity = useEntity()

  const goToCompanySettings = () => {
    onClose()
    navigate(`/org/${entity.id}/settings#info`)
  }

  return (
    <Portal onClose={onClose}>
      <Dialog onClose={onClose}>
        <header>
          <h1>
            {t("Mise à jour des informations de ma société sur CarbuRe")}{" "}
          </h1>
        </header>

        <main>
          <section>
            <p>
              <Trans>
                Il est désormais obligatoire de déclarer le n° d'enregistrement
                de votre société (SIREN ou équivalent) et de compléter les
                autres informations la concernant sur CarbuRe.
              </Trans>
            </p>
          </section>

          <section>
            <Alert
              variant="warning"
              icon={AlertCircle}
              label={t("Informations manquantes.")}
            >
              <p>
                <Trans>
                  Veuillez compléter les informations suivantes concernant votre
                  société :
                </Trans>
              </p>
              <ul>
                {!entity.registration_id && (
                  <li>
                    <Trans>
                      N° d'enregistrement de la société (SIREN ou équivalent)
                    </Trans>
                  </li>
                )}
                {!entity.registered_address && (
                  <li>
                    <Trans>Adresse de la société</Trans>
                  </li>
                )}
                {!entity.registered_city && (
                  <li>
                    <Trans>Ville de la société</Trans>
                  </li>
                )}
                {!entity.registered_country && (
                  <li>
                    <Trans>Pays de la société</Trans>
                  </li>
                )}
                {!entity.registered_zipcode && (
                  <li>
                    <Trans>Code postal de la société</Trans>
                  </li>
                )}
                {!entity.sustainability_officer && (
                  <li>
                    <Trans>Nom du contact principal</Trans>
                  </li>
                )}
                {!entity.sustainability_officer_email && (
                  <li>
                    <Trans>Email du contact principal</Trans>
                  </li>
                )}
                {!entity.sustainability_officer_phone_number && (
                  <li>
                    <Trans>Téléphone du contact principal</Trans>
                  </li>
                )}
                {!entity.activity_description && (
                  <li>
                    <Trans>Description de la société</Trans>
                  </li>
                )}
              </ul>
            </Alert>
          </section>
        </main>

        <footer>
          <Button
            asideX
            action={goToCompanySettings}
            icon={Plus}
            variant="primary"
            label={t("Compléter les informations de ma société")}
          />
        </footer>
      </Dialog>
    </Portal>
  )
}
export default CompanyInfoMissingSirenDialog
