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

export const CompanyRegistrationDialog = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const entity = useEntity()
  const searchSirentRef = useRef<HTMLElement>(null)
  const [sirenQuety, setSirenQuery] = React.useState<string>("")
  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }



  const findCompanyBySiren = (siren: string | undefined) => {
    siren = siren?.trim() || ""
    setSirenQuery(siren)

    const sirenInput = searchSirentRef.current?.querySelector('input')
    if (!sirenInput || siren.length < 3) return

    if (siren.match(/^\d{9}$/) === null) {
      sirenInput.setCustomValidity("Le SIREN doit contenir 9 chiffres")
      sirenInput.reportValidity()
      return
    }

    sirenInput.setCustomValidity("")
    sirenInput.reportValidity()

    // https://recherche-entreprises.api.gouv.fr/search?q=damien%20romito
    // #api
    api.searchCompanyData(siren).then((result) => {
      console.log('result:', result)
    })

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
            <TextInput
              required
              autoFocus
              value={sirenQuety}
              label={t("SIREN de votre entreprise ")}
              onChange={findCompanyBySiren}
              domRef={searchSirentRef}
              name="siren"
            />
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
