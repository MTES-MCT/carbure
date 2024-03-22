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
import { useMutation, useQuery } from "common/hooks/async"
import React, { useRef, useState } from "react"
import { Normalizer } from "common/utils/normalize"
import { SearchCompanyResult } from "companies/types"
import { set } from "date-fns"
import { SirenPicker } from "./siren-picker"
import { useForm } from "common/components/form"
import CompanyForm, { CompanyFormValue, useCompanyForm } from "./company-form"
import { useNotify } from "common/components/notifications"

export const CompanyRegistrationDialog = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const notify = useNotify()

  const [prefetchedCompany, setPrefetchedCompany] = useState<SearchCompanyResult | undefined>(undefined)

  // const companyApplicationResponse = useMutation(api.applyNewCompany)
  const closeDialog = () => {
    navigate("/account/")
  }

  const fillFormWithfoundCompany = (company: SearchCompanyResult) => {
    setPrefetchedCompany(company)
    notify(t("Les informations ont été remplis avec les données de l'api entreprises"), {
      variant: "success",
    })
  }

  const onSubmitForm = (value: CompanyFormValue | undefined) => {
    console.log('value:', value)
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
            {!prefetchedCompany &&
              <SirenPicker onSelect={fillFormWithfoundCompany} />
            }
            {prefetchedCompany &&
              <PrefetchedCompanyForm prefetchedCompany={prefetchedCompany} onSubmitForm={onSubmitForm} />
            }
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


interface PrefetchedCompanyFormProps {
  onSubmitForm: (formEntity: CompanyFormValue | undefined) => void
  prefetchedCompany: SearchCompanyResult
}

const PrefetchedCompanyForm = ({
  onSubmitForm,
  prefetchedCompany
}: PrefetchedCompanyFormProps) => {
  const companyForm = useCompanyForm(prefetchedCompany)
  return <CompanyForm form={companyForm!} onSubmitForm={onSubmitForm} isNew />
}