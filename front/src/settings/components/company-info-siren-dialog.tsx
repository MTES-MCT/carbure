import { AxiosError } from "axios"
import Alert from "common/components/alert"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import {
  AlertCircle,
  Plus
} from "common/components/icons"
import { useNotify, useNotifyError } from "common/components/notifications"
import Portal from "common/components/portal"
import { useMutation } from "common/hooks/async"
import * as api from "companies/api"
import { SearchCompanyPreview } from "companies/types"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import { SirenPicker } from "../../companies/components/siren-picker"

interface CompanyInfoSirenDialogProps {
  onClose: () => void
  wantPrefillCompanyInfo: (prefetchedCompany: SearchCompanyPreview) => void
}

export const CompanyInfoSirenDialog = ({
  onClose,
  wantPrefillCompanyInfo,
}: CompanyInfoSirenDialogProps
) => {
  const { t } = useTranslation()

  const notify = useNotify()
  const [prefetchedCompany, setPrefetchedCompany] = useState<SearchCompanyPreview | undefined>(undefined)
  const [prefetchedCompanyWarning, setPrefetchedCompanyWarning] = useState<string | undefined>(undefined)


  const fillFormWithFoundCompany = (company?: SearchCompanyPreview, warning?: string) => {

    if (company) {
      setPrefetchedCompanyWarning(undefined)
      notify(t("Les informations ont été pré-remplies avec les informations de l'entreprises"), {
        variant: "success",
      })
    }
    if (warning) {
      setPrefetchedCompanyWarning(warning)
    }
    setPrefetchedCompany(company)
  }

  const onSubmit = () => {
    wantPrefillCompanyInfo(prefetchedCompany!)
    onClose()
  }


  return (
    <Portal onClose={onClose}>
      <Dialog onClose={onClose}>
        <header>
          <h1>{t("Trouver ma société")} </h1>
        </header>

        <main>
          <section>
            <p>
              <Trans>Rechercher votre société dans la base de données entreprises.data.gouv :</Trans>
            </p>
          </section>
          <section>
            <SirenPicker onSelect={fillFormWithFoundCompany} />

            {prefetchedCompany && (
              <>
                <p>{prefetchedCompany.legal_name} ({prefetchedCompany.registered_address} {prefetchedCompany.registered_zipcode} {prefetchedCompany.registered_city})</p>
              </>
            )
            }
            {prefetchedCompanyWarning &&
              <Alert icon={AlertCircle} variant="warning">
                {prefetchedCompanyWarning}
              </Alert>
            }

          </section>

          {!prefetchedCompany && (
            <section>
              <Alert icon={AlertCircle} variant="info">
                <Trans>Votre société n'est pas immatriculée en France ? Choisissez votre pays dans le formulaire afin de remplir manuellement les données associées.</Trans>
              </Alert>
            </section>
          )}

        </main>

        <footer>

          <Button
            asideX
            action={onSubmit}
            disabled={!prefetchedCompany}
            icon={Plus}
            variant="primary"
            label={t("Remplir les données")}
          />
        </footer>

      </Dialog>
    </Portal >
  )
}
export default CompanyInfoSirenDialog