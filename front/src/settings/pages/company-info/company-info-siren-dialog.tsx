import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { useNotify } from "common/components/notifications"
import Portal from "common/components/portal"
import { SearchCompanyPreview } from "companies/types"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { SirenPicker } from "common/molecules/siren-picker"
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
        size="medium"
      >
        <p>
          <Trans>
            Rechercher votre société dans la base de données
            entreprises.data.gouv :
          </Trans>
        </p>
        <SirenPicker onSelect={fillFormWithFoundCompany} />

        {/* Display the company name if it exists and no warning */}
        {prefetchedCompany && !prefetchedCompanyWarning && (
          <p style={{ marginTop: "4px" }}>
            {prefetchedCompany.legal_name} (
            {prefetchedCompany.registered_address}{" "}
            {prefetchedCompany.registered_zipcode}{" "}
            {prefetchedCompany.registered_city})
          </p>
        )}
        {prefetchedCompanyWarning && (
          <Notice
            variant="warning"
            icon="ri-error-warning-line"
            title={t("Ce SIREN est déjà utilisé")}
          >
            <p style={{ marginTop: "4px" }}>{prefetchedCompanyWarning}</p>
          </Notice>
        )}

        {!prefetchedCompany && (
          <Notice
            icon="ri-error-warning-line"
            variant="info"
            title={t("Votre société n'est pas immatriculée en France ?")}
          >
            <p style={{ marginTop: "4px" }}>
              <Trans>
                Choisissez votre pays dans le formulaire afin de remplir
                manuellement les données associées.
              </Trans>
            </p>
          </Notice>
        )}
      </Dialog>
    </Portal>
  )
}
export default CompanyInfoSirenDialog
