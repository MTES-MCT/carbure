import { useMutation } from "common/hooks/async"
import * as api from "../api"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useTranslation } from "react-i18next"
import { AxiosError } from "axios"
import { CompanyRegistrationFormValue } from "companies/types"

type RegisterCompanyProps = {
  closeDialog?: () => void
}

export const useRegisterCompany = ({ closeDialog }: RegisterCompanyProps) => {
  const notify = useNotify()
  const notifyError = useNotifyError()
  const { t } = useTranslation()

  const onSubmitForm = (
    formValue: CompanyRegistrationFormValue | undefined
  ) => {
    if (!formValue) return
    registerCompanyRequest.execute(
      formValue.activity_description!,
      formValue.entity_type!,
      formValue.legal_name!,
      formValue.name!,
      formValue.registered_address!,
      formValue.registered_city!,
      formValue.registered_country?.code_pays || "",
      formValue.registered_zipcode!,
      formValue.registration_id!,
      formValue.sustainability_officer_email!,
      formValue.sustainability_officer_phone_number!.trim(),
      formValue.sustainability_officer!,
      formValue.website!,
      formValue.vat_number!,
      formValue.certificate?.certificate_id,
      formValue.certificate?.certificate_type
    )
  }
  const registerCompanyRequest = useMutation(api.registerCompany, {
    invalidates: ["user-settings"],
    onSuccess: () => {
      notify(t("Votre demande d'inscription a bien été envoyée !"), {
        variant: "success",
      })
      closeDialog?.()
    },
    onError: (err) => {
      const errorCode = (err as AxiosError<{ error: string }>).response?.data
        .error
      if (errorCode === "COMPANY_NAME_ALREADY_USED") {
        notifyError(
          err,
          t("Ce nom de société est déjà utilisé. Veuillez en choisir un autre.")
        )
      } else {
        notifyError(err)
      }
    },
  })

  return { registerCompanyRequest, onSubmitForm }
}
