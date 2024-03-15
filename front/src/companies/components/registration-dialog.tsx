import useEntity from "carbure/hooks/entity"
import Autocomplete from "common/components/autocomplete"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import {
  Return
} from "common/components/icons"
import { TextInput } from "common/components/input"
import Portal from "common/components/portal"
import { Trans, useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "companies/api"
import { useQuery } from "common/hooks/async"
import React, { useRef } from "react"
import { Normalizer } from "common/utils/normalize"
import { CompanyResult } from "companies/types"
import { searchCompanyResult } from "companies/__test__/data"

export const CompanyRegistrationDialog = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  const fillFormWithfoundCompany = (company: CompanyResult) => {
    console.log('company:', company)
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog fullscreen onClose={closeDialog}>
        <header>
          <h1>{t("Inscrire ma société sur CarbuRe")} </h1>
        </header>

        <main>

          <section>
            <p>
              <Trans>Rechercher votre société dans la base de donnée entreprises.data.gouv :</Trans>
            </p>
          </section>
          <section>
            <SirenPicker onSelect={fillFormWithfoundCompany} />
          </section>
          <section>
            {/* #form */}
          </section>

        </main>

        <footer>

          <Button icon={Return} action={closeDialog}>
            <Trans>Retour</Trans>
          </Button>
        </footer>

      </Dialog>
    </Portal >
  )
}

interface SirenPickerProps {
  onSelect?: (company: CompanyResult) => void
}
const SirenPicker = ({
  onSelect
}: SirenPickerProps) => {
  const { t } = useTranslation()
  const searchSirentRef = useRef<HTMLInputElement>(null)
  const [sirenQuery, setSirenQuery] = React.useState<CompanyResult | string | undefined>("")
  const [searchCompanyResult, setSearchCompanyResult] = React.useState<CompanyResult[]>([])

  const findCompanyOnQuery = (siren: string) => {

    setSirenQuery(siren)

  }
  console.log('siren:', sirenQuery)

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
    console.log('company:', company)
  }

  return <section>

    <Autocomplete
      autoFocus
      value={sirenQuery}
      label={t("SIREN de votre entreprise :")}
      normalize={normalizeCompanyResult}
      onSelect={selectCompany}
      // onQuery={findCompanyOnQuery}
      getOptions={getCompanies}
      inputRef={searchSirentRef}
    />
  </section>
}