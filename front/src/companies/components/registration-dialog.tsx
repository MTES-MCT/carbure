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
import { set } from "date-fns"
import { SirenPicker } from "./siren-picker"
import { useForm } from "common/components/form"
import CompanyForm, { CompanyFormValue, useCompanyForm } from "./company-form"

export const CompanyRegistrationDialog = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const entity = useEntity()
  const { value, bind } = useForm({
    siret: "" as string | undefined,

  })
  const closeDialog = () => {
    navigate("/account/")
  }

  const fillFormWithfoundCompany = (company: CompanyResult) => {
    console.log('>>company:', company)
  }

  const onSubmitForm = (ormEntity: CompanyFormValue | undefined) => {
  }

  const form = useCompanyForm(entity)

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
            <CompanyForm form={form} entity={entity} onSubmitForm={onSubmitForm} />

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
