import Dialog from "common/components/dialog"
import { useTranslation } from "react-i18next"
import { CompanyForm } from "./company-form"
import Button from "common/components/button"
import { Plus } from "common/components/icons"
import { useRegisterCompany } from "./registration-dialog.hooks"

type ForeignCompanyDialogProps = {
  close: () => void
}

export const ForeignCompanyDialog = ({ close }: ForeignCompanyDialogProps) => {
  const { t } = useTranslation()
  const { registerCompanyRequest, onSubmitForm } = useRegisterCompany({
    closeDialog: close,
  })

  return (
    <Dialog onClose={close}>
      <header>
        <h1>{t("Inscrire ma société sur CarbuRe - Hors France")} </h1>
      </header>

      <main>
        <section>
          <CompanyForm
            onSubmitForm={onSubmitForm}
            formId="foreign-company-form"
            isForeignCompany
          />
        </section>
      </main>

      <footer>
        <Button
          asideX
          submit="foreign-company-form"
          loading={registerCompanyRequest.loading}
          icon={Plus}
          variant="primary"
          label={t("Demander l'inscription de votre société")}
        />
      </footer>
    </Dialog>
  )
}
