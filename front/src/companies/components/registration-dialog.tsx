import Alert from "common/components/alert"
import { Button, MailTo } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { AlertCircle, Plus } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import Portal, { usePortal } from "common/components/portal"

import { SearchCompanyPreview } from "companies/types"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import { SirenPicker } from "./siren-picker"
import { ForeignCompanyDialog } from "./foreign-company-dialog"
import { CompanyForm } from "./company-form"
import { useRegisterCompany } from "./registration-dialog.hooks"

export const CompanyRegistrationDialog = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const portal = usePortal()
  const notify = useNotify()
  const [prefetchedCompany, setPrefetchedCompany] = useState<
    SearchCompanyPreview | undefined
  >(undefined)
  const [prefetchedCompanyWarning, setPrefetchedCompanyWarning] = useState<
    string | undefined
  >(undefined)

  const closeDialog = () => {
    navigate("/account/")
  }

  const { registerCompanyRequest, onSubmitForm } = useRegisterCompany({
    closeDialog,
  })

  const fillFormWithFoundCompany = (
    company?: SearchCompanyPreview,
    warning?: string
  ) => {
    if (company) {
      setPrefetchedCompanyWarning(undefined)
      notify(
        t(
          "Les informations ont été pré-remplies avec les données de l'entreprises"
        ),
        {
          variant: "success",
        }
      )
    }
    if (warning) {
      setPrefetchedCompanyWarning(warning)
    }
    setPrefetchedCompany(company)
  }

  const openForeignCompanyDialog = () => {
    portal((close) => <ForeignCompanyDialog close={close} />)
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog}>
        <header>
          <h1>{t("Inscrire ma société sur CarbuRe")} </h1>
        </header>

        <main>
          <section>
            <p>
              <Trans>
                Rechercher votre société dans la base de donnée
                entreprises.data.gouv :
              </Trans>
            </p>
          </section>
          <section>
            {!prefetchedCompany && (
              <SirenPicker onSelect={fillFormWithFoundCompany} />
            )}
            {prefetchedCompanyWarning && (
              <Alert icon={AlertCircle} variant="warning">
                {prefetchedCompanyWarning}
              </Alert>
            )}
            {prefetchedCompany && (
              <CompanyForm
                company={prefetchedCompany}
                onSubmitForm={onSubmitForm}
              />
            )}
          </section>

          <section>
            <p>
              <Trans>Votre société n’est pas immatriculée en France ? </Trans>
              <Button variant="link" action={openForeignCompanyDialog}>
                <Trans>Ajoutez une société étrangère</Trans>
              </Button>
            </p>
            <p>
              <Trans>Vous ne trouvez pas votre société ? </Trans>
              <MailTo
                user="carbure"
                host="beta.gouv.fr"
                subject={t(
                  "[CarbuRe - Société] Je souhaite ajouter une société"
                )}
                body={t(
                  "Bonjour%2C%E2%80%A8%E2%80%A8Je%20souhaite%20ajouter%20ma%20soci%C3%A9t%C3%A9%20sur%20CarbuRe%20mais%20celle-ci%20est%20introuvable%20dans%20la%20base%20de%20donn%C3%A9es.%20Voici%20les%20informations%20la%20concernant%20%3A%0D%0A%0D%0A1%20-%20Nom%20de%20la%20soci%C3%A9t%C3%A9%20%3A%0D%0A%0D%0A2%20-%20Description%20de%20l'activit%C3%A9%20(obligatoire)%20%3A%0D%0A%0D%0A3%20-%20SIREN%20%3A%0D%0A%0D%0A4%20-%20Adresse%20postale%20%3A%E2%80%A8%0D%0AMerci%20beaucoup%E2%80%A8Bien%20cordialement%2C"
                )}
              >
                <Trans>Signalez un problème.</Trans>
              </MailTo>
            </p>
          </section>
        </main>

        <footer>
          <Button
            asideX
            submit="add-company"
            loading={registerCompanyRequest.loading}
            disabled={!prefetchedCompany}
            icon={Plus}
            variant="primary"
            label={t("Demander l'inscription de votre société")}
          />
        </footer>
      </Dialog>
    </Portal>
  )
}
