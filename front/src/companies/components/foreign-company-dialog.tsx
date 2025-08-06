import { Dialog } from "common/components/dialog2"
import { useTranslation } from "react-i18next"
import { CompanyForm } from "./company-form"
import { Button } from "common/components/button2"
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
    <Dialog
      onClose={close}
      header={
        <Dialog.Title>
          {t("Inscrire ma société sur CarbuRe - Hors France")}
        </Dialog.Title>
      }
      footer={
        <Button
          asideX
          loading={registerCompanyRequest.loading}
          iconId="ri-add-line"
          type="submit"
          nativeButtonProps={{
            form: "foreign-company-form",
          }}
        >
          {t("Demander l'inscription de votre société")}
        </Button>
      }
      size="medium"
    >
      <CompanyForm
        onSubmitForm={onSubmitForm}
        formId="foreign-company-form"
        isForeignCompany
      />
    </Dialog>
  )
}
