import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { useNotify } from "common/components/notifications"
import Portal from "common/components/portal"

import { SearchCompanyMeta, SearchCompanyPreview } from "companies/types"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import { SirenPicker } from "common/molecules/siren-picker"
import { CompanyForm } from "./company-form"
import { useRegisterCompany } from "./registration-dialog.hooks"
import { Notice } from "common/components/notice"
import { ROUTE_URLS } from "common/utils/routes"

export const CompanyRegistrationDialog = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const notify = useNotify()
  const [prefetchedCompany, setPrefetchedCompany] = useState<
    SearchCompanyPreview | undefined
  >(undefined)
  const [prefetchedCompanyWarning, setPrefetchedCompanyWarning] = useState<
    string | undefined
  >(undefined)
  const [prefetchedCompanyError, setPrefetchedCompanyError] = useState<
    React.ReactNode | undefined
  >(undefined)

  const closeDialog = () => {
    navigate(ROUTE_URLS.MY_ACCOUNT.COMPANIES)
  }

  const { registerCompanyRequest, onSubmitForm } = useRegisterCompany({
    closeDialog,
  })

  const fillFormWithFoundCompany = (
    company?: SearchCompanyPreview,
    warning?: string,
    meta?: SearchCompanyMeta
  ) => {
    setPrefetchedCompanyError(undefined)
    if (meta?.entities && meta?.entities.length > 0) {
      const hasOnlyOneEntity = meta?.entities.length === 1
      const message = (
        <div>
          {hasOnlyOneEntity ? (
            <p>
              {t(
                "Ce SIREN est déjà utilisé par l'entité suivante : {{entityName}}",
                { entityName: meta?.company_name }
              )}
            </p>
          ) : (
            <>
              {t("Ce SIREN est déjà utilisé par les entités suivantes :")}
              <ul>
                {meta?.entities.map((entity) => (
                  <li key={entity.name}>{entity.name}</li>
                ))}
              </ul>
            </>
          )}

          <Trans
            defaults="Vous pouvez rechercher et demander à rejoindre la société en cliquant <Link>sur ce lien</Link>. Votre DREAL sera informée de l'inscription et validera votre demande."
            components={{
              Link: (
                // @ts-ignore children is propagated to the button by i18next
                <Button
                  customPriority="link"
                  linkProps={{ to: ROUTE_URLS.MY_ACCOUNT.ADD_COMPANY }}
                />
              ),
            }}
          ></Trans>
        </div>
      )
      setPrefetchedCompanyError(message)
      return
    }
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

  return (
    <Portal onClose={closeDialog}>
      <Dialog
        onClose={closeDialog}
        header={
          <>
            <Dialog.Title>{t("Inscrire ma société sur CarbuRe")} </Dialog.Title>
            <Dialog.Description>
              <Trans>
                Rechercher votre société dans la base de donnée
                entreprises.data.gouv :
              </Trans>
            </Dialog.Description>
          </>
        }
        footer={
          <Button
            asideX
            loading={registerCompanyRequest.loading}
            disabled={!prefetchedCompany}
            iconId="ri-add-line"
            type="submit"
            nativeButtonProps={{
              form: "add-company",
            }}
          >
            {t("Demander l'inscription de votre société")}
          </Button>
        }
        size="medium"
      >
        {!prefetchedCompany && (
          <SirenPicker onSelect={fillFormWithFoundCompany} />
        )}
        {prefetchedCompanyError && (
          <Notice variant="warning" icon="ri-error-warning-line">
            {prefetchedCompanyError}
          </Notice>
        )}
        {prefetchedCompanyWarning && (
          <Notice variant="warning" icon="ri-error-warning-line">
            {prefetchedCompanyWarning}
          </Notice>
        )}
        {prefetchedCompany && (
          <CompanyForm
            company={prefetchedCompany}
            onSubmitForm={onSubmitForm}
          />
        )}

        <p>
          <Trans>Votre société n’est pas immatriculée en France ?</Trans>
          <Button
            customPriority="link"
            linkProps={{
              to: ROUTE_URLS.MY_ACCOUNT.FOREIGN_COMPANY_REGISTRATION,
            }}
          >
            <Trans>Ajoutez une société étrangère</Trans>
          </Button>
        </p>
        <p>
          <Trans>Vous ne trouvez pas votre société ? </Trans>
          <Button
            customPriority="link"
            linkProps={{
              to: ROUTE_URLS.CONTACT,
            }}
          >
            <Trans>Contactez-nous.</Trans>
          </Button>
        </p>
      </Dialog>
    </Portal>
  )
}
