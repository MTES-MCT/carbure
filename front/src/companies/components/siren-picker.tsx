import Autocomplete from "common/components/autocomplete"
import { Normalizer } from "common/utils/normalize"
import * as api from "companies/api"
import { CompanyResult } from "companies/types"
import React, { useRef } from "react"
import { useTranslation } from "react-i18next"


interface SirenPickerProps {
  onSelect: (company: CompanyResult) => void
}
export const SirenPicker = ({
  onSelect
}: SirenPickerProps) => {
  const { t } = useTranslation()
  const searchSirentRef = useRef<HTMLInputElement>(null)
  const [sirenQuery, setSirenQuery] = React.useState<CompanyResult | string | undefined>("")
  const [searchCompanyResult, setSearchCompanyResult] = React.useState<CompanyResult[]>([])

  const checkSirenFormat = (siren: string) => {
    siren = siren?.trim() || ""

    const sirenInput = searchSirentRef.current
    console.log('sirenInput:', sirenInput)
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
  const getCompanies = async (siren: string) => {

    if (!checkSirenFormat(siren)) return new Promise<CompanyResult[]>((resolve) => {
      resolve([])
    })

    // https://recherche-entreprises.api.gouv.fr/search?q=damien%20romito
    // #api
    const companies = await api.searchCompanyData(siren)
    setSearchCompanyResult(companies)
    return companies
    // return new Promise<CompanyResult[]>((resolve) => {
    //   resolve(searchCompanyResult)
    // })

  }

  const normalizeCompanyResult: Normalizer<CompanyResult, string> = (result: CompanyResult) => ({
    value: result?.siren,
    label: `${result?.nom_complet} (${result?.siren})`,
  })

  const selectCompany = (siren: string | undefined | CompanyResult) => {
    const company = searchCompanyResult.find((c) => c.siren === siren)
    if (!company) return
    onSelect(company)
  }

  return <section>

    <Autocomplete
      autoFocus
      // value={sirenQuery}
      label={t("SIREN de votre entreprise :")}
      normalize={normalizeCompanyResult}
      onSelect={selectCompany}
      // onQuery={findCompanyOnQuery}
      getOptions={getCompanies}
      inputRef={searchSirentRef}
    />
  </section>
}