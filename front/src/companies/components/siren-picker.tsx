import { AxiosError } from "axios"
import { TextInput } from "common/components/input"
import { useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import * as api from "companies/api"
import { SearchCompanyPreview } from "companies/types"
import { useRef, useState } from "react"
import { useTranslation } from "react-i18next"


interface SirenPickerProps {
  onSelect: (company?: SearchCompanyPreview, warning?: string) => void
}
export const SirenPicker = ({
  onSelect
}: SirenPickerProps) => {
  const { t } = useTranslation()
  const searchSirentRef = useRef<HTMLInputElement>(null)
  const [siren, setSiren] = useState<string | undefined>("")
  const notifyError = useNotifyError()
  const [error, setError] = useState<string | undefined>(undefined)
  const companyResponse = useMutation(api.searchCompanyDataBySiren, {
    onSuccess: (res) => {
      const companyResult = res.data.data

      if (!companyResult) return
      let warning
      if (companyResult.warning?.code === "REGISTRATION_ID_ALREADY_USED") {
        warning = t("Ce SIREN existe déjà dans notre base CarbuRe, sous le nom de {{companyName}}. Assurez-vous que cela soit bien votre entreprise avant de continuer et utilisez un nom différent.", { companyName: companyResult.warning.meta.company_name })
      }
      onSelect(companyResult.company_preview, warning)
      setError(undefined)

    },
    onError: (err) => {
      const error = (err as AxiosError<{ error: string }>).response?.data.error
      if (error === 'NO_COMPANY_FOUND') {
        const message = t("Aucune entreprise n'a été trouvée avec ce numéro de SIREN")
        notifyError(err, message)
        onSelect()
        setError(message)
        return
      }
      notifyError(err)
    },
  })

  const checkSirenFormat = (siren: string) => {

    const sirenInput = searchSirentRef.current
    if (!sirenInput || siren.length < 3) return false

    if (siren.match(/^\d{9}$/) === null) {
      sirenInput.setCustomValidity("Ce SIREN est invalide. Il doit être constitué 9 caractères numériques.")
      sirenInput.reportValidity()
      return false
    }
    sirenInput.setCustomValidity("")
    sirenInput.reportValidity()
    return true
  }

  const typeSiren = async (siren: string | undefined) => {
    siren = siren?.trim() || ""
    setSiren(siren)
    if (!checkSirenFormat(siren)) return
    companyResponse.execute(siren)
  }


  return <section>
    <TextInput
      autoFocus
      loading={companyResponse.loading}
      value={siren}
      error={error}
      type="siren"
      label={t("SIREN de votre entreprise")}
      onChange={typeSiren}
      inputRef={searchSirentRef}
    />
  </section>
}