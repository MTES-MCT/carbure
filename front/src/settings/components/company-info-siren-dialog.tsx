import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { useNotify } from "common/components/notifications"
import Portal from "common/components/portal"
import { SearchCompanyPreview } from "companies/types"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { SirenPicker } from "../../companies/components/siren-picker"
import { Notice } from "common/components/notice"

interface CompanyInfoSirenDialogProps {
  onClose: () => void
  wantPrefillCompanyInfo: (prefetchedCompany: SearchCompanyPreview) => void
}

export const CompanyInfoSirenDialog = ({
  onClose,
  wantPrefillCompanyInfo,
}: CompanyInfoSirenDialogProps) => {
  const { t } = useTranslation()

  const notify = useNotify()
  const [prefetchedCompany, setPrefetchedCompany] = useState<
    SearchCompanyPreview | undefined
  >(undefined)
  const [prefetchedCompanyWarning, setPrefetchedCompanyWarning] = useState<
    string | undefined
  >(undefined)

  const fillFormWithFoundCompany = (
    company?: SearchCompanyPreview,
    warning?: string
  ) => {
    if (company) {
      setPrefetchedCompanyWarning(undefined)
      notify(
        t(
          "Les informations ont été pré-remplies avec les informations de l'entreprises"
        ),
        {
          variant: "success",
        }
      )
    }

    setPrefetchedCompanyWarning(warning ?? undefined)

    setPrefetchedCompany(company)
  }

  const onSubmit = () => {
    wantPrefillCompanyInfo(prefetchedCompany!)
    onClose()
  }

  return (
    <Portal onClose={onClose}>
      <Dialog
        onClose={onClose}
        header={<Dialog.Title>{t("Trouver ma société")}</Dialog.Title>}
        footer={
          <Button
            asideX
            onClick={onSubmit}
            disabled={!prefetchedCompany}
            iconId="ri-add-line"
          >
            {t("Remplir les données")}
          </Button>
        }
      >
        <p>
          <Trans>
            Rechercher votre société dans la base de données
            entreprises.data.gouv :
          </Trans>
        </p>
        <SirenPicker onSelect={fillFormWithFoundCompany} />

        {prefetchedCompany && (
          <p>
            {prefetchedCompany.legal_name} (
            {prefetchedCompany.registered_address}{" "}
            {prefetchedCompany.registered_zipcode}{" "}
            {prefetchedCompany.registered_city})
          </p>
        )}
        {prefetchedCompanyWarning && (
          <Notice variant="warning" icon="ri-error-warning-line">
            {prefetchedCompanyWarning}
          </Notice>
        )}

        {!prefetchedCompany && (
          <Notice icon="ri-error-warning-line" variant="info">
            <Trans>
              Votre société n'est pas immatriculée en France ? Choisissez votre
              pays dans le formulaire afin de remplir manuellement les données
              associées.
            </Trans>
          </Notice>
        )}
      </Dialog>
    </Portal>
  )
}
export default CompanyInfoSirenDialog
