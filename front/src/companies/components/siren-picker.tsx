import useEntity from "carbure/hooks/entity"
import Autocomplete from "common/components/autocomplete"
import { TextInput } from "common/components/input"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { Normalizer } from "common/utils/normalize"
import * as api from "companies/api"
import { CompanyResult } from "companies/types"
import React, { useRef, useState } from "react"
import { useTranslation } from "react-i18next"


interface SirenPickerProps {
  onSelect: (company: CompanyResult) => void
}
export const SirenPicker = ({
  onSelect
}: SirenPickerProps) => {
  const { t } = useTranslation()
  const searchSirentRef = useRef<HTMLInputElement>(null)
  const [siren, setSiren] = useState<string | undefined>("")
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()

  const companyResponse = useMutation(api.getCompanyDataBySiren, {
    onSuccess: (res) => {
      console.log('res:', res)
      notify(t("Les informations ont été remplis avec les données de l'api entreprise"), {
        variant: "success",
      })
    },
    onError: (err) => {
      notifyError(err)
    },
  })

  const checkSirenFormat = (siren: string) => {

    const sirenInput = searchSirentRef.current
    if (!sirenInput || siren.length < 3) return false

    if (siren.match(/^\d{9}$/) === null) {
      sirenInput.setCustomValidity("Le SIREN doit contenir 9 chiffres")
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
    const response = await companyResponse.execute(entity.id, siren)
    console.log('response:', response)
    //   onSelect(company)
  }


  return <section>

    <TextInput
      autoFocus
      value={siren}
      type="siren"
      label={t("SIREN de votre entreprise")}
      onChange={typeSiren}
      inputRef={searchSirentRef}
    />

  </section>
}