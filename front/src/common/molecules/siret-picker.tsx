import { TextInput, TextInputProps } from "common/components/inputs2"
import { useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { HttpError } from "common/services/api-fetch"
import { searchCompanyData } from "common/api"
import { SearchCompanyPreview } from "companies/types"
import { useRef, useState } from "react"
import { useTranslation } from "react-i18next"

interface SiretPickerProps extends TextInputProps {
  onSelect: (company?: SearchCompanyPreview) => void
}

export const SiretPicker = ({ onSelect, ...props }: SiretPickerProps) => {
  const { t } = useTranslation()
  const searchSiretRef = useRef<HTMLInputElement>(null)
  const notifyError = useNotifyError()
  const [error, setError] = useState<string | undefined>(undefined)
  const companyResponse = useMutation(searchCompanyData, {
    onSuccess: (res) => {
      const companyResult = res.data

      if (!companyResult) return

      onSelect(companyResult.company_preview)
      setError(undefined)
    },
    onError: (err) => {
      onSelect()
      const error = (err as HttpError).data.error

      if (error === "NO_COMPANY_FOUND") {
        const message = t(
          "Aucune entreprise n'a été trouvée avec ce numéro SIRET"
        )
        notifyError(err, message)

        setError(message)
        return
      }
      notifyError(err)
    },
  })

  const checkSiretFormat = (siret: string) => {
    const siretInput = searchSiretRef.current
    if (!siretInput) return false

    if (siret.match(/^\d{14}$/) === null) {
      siretInput.setCustomValidity(
        "Ce SIRET est invalide. Il doit être constitué de 14 caractères numériques."
      )
      siretInput.reportValidity()
      return false
    }
    siretInput.setCustomValidity("")
    siretInput.reportValidity()
    return true
  }

  const typeSiret = async (siret: string | undefined) => {
    siret = siret?.trim() || ""
    props.onChange?.(siret)
    if (!checkSiretFormat(siret)) return
    companyResponse.execute(siret)
  }

  const onPasteSiret = (
    value: string | undefined,
    event: React.ClipboardEvent<HTMLInputElement>
  ) => {
    const formattedSiret = value?.replaceAll(" ", "") || ""
    typeSiret(formattedSiret)
    event.preventDefault()
  }

  return (
    <TextInput
      {...props}
      loading={companyResponse.loading}
      state={error ? "error" : undefined}
      stateRelatedMessage={error}
      type="siret"
      label={props.label ?? t("SIRET de votre entreprise")}
      onChange={typeSiret}
      onPaste={onPasteSiret}
      inputRef={searchSiretRef}
    />
  )
}
