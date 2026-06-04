import { COMMON_QUERY_KEYS, useMutation } from "common/hooks/async-rq"
import * as api from "../api"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useTranslation } from "react-i18next"
import { AxiosError } from "axios"
import {
  CompanyRegistrationFormValue,
  RegisterCompanyPayload,
} from "companies/types"

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
    const payload = toRegisterCompanyPayload(formValue)
    if (!payload) return
    registerCompanyRequest.execute(payload)
  }
  const registerCompanyRequest = useMutation(api.registerCompany, {
    invalidates: [COMMON_QUERY_KEYS.userSettings],
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

function toRegisterCompanyPayload(
  formValue: CompanyRegistrationFormValue | undefined
): RegisterCompanyPayload | undefined {
  if (!formValue || !canBuildRegisterCompanyPayload(formValue)) return

  return {
    ...formValue,
    registration_id: formValue.registration_id ?? "",
    sustainability_officer_phone_number:
      formValue.sustainability_officer_phone_number.trim(),
    certificate_id: formValue.certificate?.certificate_id,
    certificate_type: formValue.certificate?.certificate_type,
  }
}

function canBuildRegisterCompanyPayload(
  formValue: CompanyRegistrationFormValue
): formValue is RegisterCompanyPayload {
  return Boolean(
    formValue.activity_description &&
    formValue.entity_type &&
    formValue.legal_name &&
    formValue.name &&
    formValue.registered_address &&
    formValue.registered_city &&
    formValue.registered_country &&
    formValue.registered_zipcode &&
    formValue.sustainability_officer_email &&
    formValue.sustainability_officer_phone_number &&
    formValue.sustainability_officer
  )
}
