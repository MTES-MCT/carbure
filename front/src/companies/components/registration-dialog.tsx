import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { useNotify } from "common/components/notifications"
import Portal, { usePortal } from "common/components/portal"

import { SearchCompanyPreview } from "companies/types"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import { SirenPicker } from "common/molecules/siren-picker"
import { ForeignCompanyDialog } from "./foreign-company-dialog"
import { CompanyForm } from "./company-form"
import { useRegisterCompany } from "./registration-dialog.hooks"
import { Notice } from "common/components/notice"
import { ROUTE_URLS } from "common/utils/routes"

export const CompanyRegistrationDialog = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const portal = usePortal()
  const notify = useNotify()
  const [prefetchedCompany, setPrefetchedCompany] = useState<
    SearchCompanyPreview | undefined
  >(undefined)
  const [prefetchedCompanyWarning, setPrefetchedCompanyWarning] = useState<
    string | undefined
  >(undefined)

  const closeDialog = () => {
    navigate(ROUTE_URLS.MY_ACCOUNT.COMPANIES)
  }

  const { registerCompanyRequest, onSubmitForm } = useRegisterCompany({
    closeDialog,
  })

  const fillFormWithFoundCompany = (
    company?: SearchCompanyPreview,
    warning?: string
  ) => {
    if (company) {
      setPrefetchedCompanyWarning(undefined)
      notify(
        t(
          "Les informations ont été pré-remplies avec les données de l'entreprises"
        ),
        {
          variant: "success",
        }
      )
    }
    if (warning) {
      setPrefetchedCompanyWarning(warning)
    }
    setPrefetchedCompany(company)
  }

  const openForeignCompanyDialog = () => {
    portal((close) => <ForeignCompanyDialog close={close} />)
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog
        onClose={closeDialog}
        header={
          <>
            <Dialog.Title>{t("Inscrire ma société sur CarbuRe")} </Dialog.Title>
            <Dialog.Description>
              <Trans>
                Rechercher votre société dans la base de donnée
                entreprises.data.gouv :
              </Trans>
            </Dialog.Description>
          </>
        }
        footer={
          <Button
            asideX
            loading={registerCompanyRequest.loading}
            disabled={!prefetchedCompany}
            iconId="ri-add-line"
            type="submit"
            nativeButtonProps={{
              form: "add-company",
            }}
          >
            {t("Demander l'inscription de votre société")}
          </Button>
        }
        size="medium"
      >
        {!prefetchedCompany && (
          <SirenPicker onSelect={fillFormWithFoundCompany} />
        )}
        {prefetchedCompanyWarning && (
          <Notice variant="warning" icon="ri-error-warning-line">
            {prefetchedCompanyWarning}
          </Notice>
        )}
        {prefetchedCompany && (
          <CompanyForm
            company={prefetchedCompany}
            onSubmitForm={onSubmitForm}
          />
        )}

        <p>
          <Trans>Votre société n’est pas immatriculée en France ? </Trans>
          <Button customPriority="link" onClick={openForeignCompanyDialog}>
            <Trans>Ajoutez une société étrangère</Trans>
          </Button>
        </p>
        <p>
          <Trans>Vous ne trouvez pas votre société ? </Trans>
          <Button
            customPriority="link"
            linkProps={{
              to: ROUTE_URLS.CONTACT,
            }}
          >
            <Trans>Contactez-nous.</Trans>
          </Button>
        </p>
      </Dialog>
    </Portal>
  )
}
