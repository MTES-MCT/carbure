import { Certificate, Country, EntityType } from "carbure/types"
import { getEntityTypeLabel, normalizeCertificate, normalizeCountry } from "carbure/utils/normalizers"
import Alert from "common/components/alert"
import Autocomplete from "common/components/autocomplete"
import { Button, MailTo } from "common/components/button"
import { Dialog } from "common/components/dialog"
import Form, { useForm } from "common/components/form"
import {
  AlertCircle,
  ExternalLink,
  Plus,
  Return
} from "common/components/icons"
import { TextArea, TextInput } from "common/components/input"
import { useNotify, useNotifyError } from "common/components/notifications"
import Portal from "common/components/portal"
import Select from "common/components/select"
import { useMutation } from "common/hooks/async"
import * as api from "companies/api"
import { CompanyRegistrationFormValue, SearchCompanyPreview } from "companies/types"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import { getCertificates } from "settings/api/certificates"
import { SirenPicker } from "./siren-picker"
import { findCountries } from "carbure/api"
import { AxiosError } from "axios"

export const CompanyRegistrationDialog = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()

  const notify = useNotify()
  const notifyError = useNotifyError()
  const [prefetchedCompany, setPrefetchedCompany] = useState<SearchCompanyPreview | undefined>(undefined)
  const [prefetchedCompanyWarning, setPrefetchedCompanyWarning] = useState<string | undefined>(undefined)
  const registerCompanyRequest = useMutation(api.registerCompany, {
    invalidates: ["user-settings"],
    onSuccess: (res) => {
      notify(t("Votre demande d'inscription a bien été envoyéeVotre demande d’inscription de société a bien été prise en compte !"), {
        variant: "success",
      })
      closeDialog()
    },
    onError: (err) => {
      const errorCode = (err as AxiosError<{ error: string }>).response?.data.error
      if (errorCode === "COMPANY_NAME_ALREADY_USED") {
        notifyError(err, t("Ce nom de société est déjà utilisé. Veuillez en choisir un autre."))
      } else {
        notifyError(err)
      }
    },
  })

  const closeDialog = () => {
    navigate("/account/")
  }

  const fillFormWithFoundCompany = (company: SearchCompanyPreview, warning?: string) => {
    setPrefetchedCompany(company)
    if (warning) {
      setPrefetchedCompanyWarning(warning)
    }
    notify(t("Les informations ont été pré-remplies avec les données de l'entreprises"), {
      variant: "success",
    })
  }

  const onSubmitForm = (formValue: CompanyRegistrationFormValue | undefined) => {
    if (!formValue) return
    registerCompanyRequest.execute(
      formValue.activity_description!,
      formValue.entity_type!,
      formValue.legal_name!,
      formValue.name!,
      formValue.registered_address!,
      formValue.registered_city!,
      formValue.registered_country?.code_pays!,
      formValue.registered_zipcode!,
      formValue.registration_id!,
      formValue.sustainability_officer_email!,
      formValue.sustainability_officer_phone_number!.trim(),
      formValue.sustainability_officer!,
      formValue.website!,
      formValue.vat_number!,
      formValue.certificate?.certificate_id,
      formValue.certificate?.certificate_type,
    )
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
              <Trans>Rechercher votre société dans la base de donnée entreprises.data.gouv :</Trans>
            </p>
          </section>
          <section>
            {!prefetchedCompany &&
              <SirenPicker onSelect={fillFormWithFoundCompany} />
            }
            {prefetchedCompanyWarning &&
              <Alert icon={AlertCircle} variant="warning">
                {prefetchedCompanyWarning}
              </Alert>
            }
            {prefetchedCompany &&
              <PrefetchedCompanyForm prefetchedCompany={prefetchedCompany} onSubmitForm={onSubmitForm} />
            }
          </section>

          <section>
            <p><Trans>Vous ne trouvez pas votre société ? </Trans>
              <MailTo user="carbure" host="beta.gouv.fr"
                subject={t("[CarbuRe - Société] Je souhaite ajouter une société")}
                body={t("Bonjour%2C%E2%80%A8%E2%80%A8Je%20souhaite%20ajouter%20ma%20soci%C3%A9t%C3%A9%20sur%20CarbuRe%20mais%20celle-ci%20est%20introuvable%20dans%20la%20base%20de%20donn%C3%A9es.%20Voici%20les%20informations%20la%20concernant%20%3A%0D%0A%0D%0A1%20-%20Nom%20de%20la%20soci%C3%A9t%C3%A9%20%3A%0D%0A%0D%0A2%20-%20Description%20de%20l'activit%C3%A9%20(obligatoire)%20%3A%0D%0A%0D%0A3%20-%20SIREN%20%3A%0D%0A%0D%0A4%20-%20Adresse%20postale%20%3A%E2%80%A8%0D%0AMerci%20beaucoup%E2%80%A8Bien%20cordialement%2C")}
              >
                <Trans>Signalez un problème.</Trans>
                <ExternalLink size={20} />
              </MailTo></p>
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
    </Portal >
  )
}


interface PrefetchedCompanyFormProps {
  onSubmitForm: (formEntity: CompanyRegistrationFormValue | undefined) => void
  prefetchedCompany: SearchCompanyPreview
}

const PrefetchedCompanyForm = ({
  onSubmitForm,
  prefetchedCompany
}: PrefetchedCompanyFormProps) => {
  const { t } = useTranslation()

  const companyForm = useCompanyForm(prefetchedCompany)


  return <>
    <Form
      form={companyForm}
      id="add-company"
      onSubmit={onSubmitForm}
    >
      <TextInput
        required
        label={t("N° d'enregistrement de la société (SIREN)")}
        {...companyForm.bind("registration_id")}
        disabled
      />
      <TextInput
        required
        label={t("Nom de la société (visible dans carbure)")}
        {...companyForm.bind("name")}
      />
      <TextInput
        required
        label={t("Nom légal")}
        {...companyForm.bind("legal_name")}
        disabled
      />
      <TextInput
        required
        label={t("Adresse de la société (Numéro et rue)")}
        {...companyForm.bind("registered_address")}
        disabled
      />
      <TextInput
        required
        label={t("Ville")}
        {...companyForm.bind("registered_city")}
        disabled
      />
      <TextInput
        required
        label={t("Code postal")}
        {...companyForm.bind("registered_zipcode")}
        disabled
      />
      <Autocomplete
        label={t("Pays")}
        placeholder={t("Rechercher un pays...")}
        getOptions={findCountries}
        normalize={normalizeCountry}
        {...companyForm.bind("registered_country")}
        disabled
      />
      <TextInput
        required
        label={t("Responsable durabilité")}
        placeholder="Jean-Pierre Champollion"
        {...companyForm.bind("sustainability_officer")}
      />
      <TextInput
        required
        type="tel"
        pattern="^\+[0-9]{1,3}\s?[0-9]{6,14}$"
        label={t("N° téléphone responsable durabilité (commence par +33 pour la France)")}
        placeholder="exemple : +33612345678"
        {...companyForm.bind("sustainability_officer_phone_number")}
      />
      <TextInput
        required
        type="email"
        label={t("Email responsable durabilité")}
        {...companyForm.bind("sustainability_officer_email")}
      />


      <Select
        required
        label={t("Type d'activité")}
        placeholder={t("Précisez le type d'activité")}
        {...companyForm.bind("entity_type")}

        options={[
          {
            value: EntityType.Producer,
            label: getEntityTypeLabel(EntityType.Producer),
          },
          {
            value: EntityType.Airline,
            label: getEntityTypeLabel(EntityType.Airline),
          },
          {
            value: EntityType.CPO,
            label: getEntityTypeLabel(EntityType.CPO),
          },
          {
            value: EntityType.Operator,
            label: getEntityTypeLabel(EntityType.Operator),
          },
          {
            value: EntityType.Trader,
            label: getEntityTypeLabel(EntityType.Trader),
          },
          {
            value: EntityType.PowerOrHeatProducer,
            label: getEntityTypeLabel(EntityType.PowerOrHeatProducer),
          },
        ]}
      />
      {companyForm.value?.entity_type && ![EntityType.Airline, EntityType.CPO].includes(companyForm.value?.entity_type) && (
        <Autocomplete
          label={t("Certificat (schéma volontaire ou national)")}
          normalize={normalizeCertificate}
          getOptions={(query) =>
            getCertificates(query).then((res) => res.data.data ?? [])
          }
          {...companyForm.bind("certificate")}

        />
      )}
      <TextArea
        required
        label={t("Description de l'activité")}
        {...companyForm.bind("activity_description")}
      />

      <TextInput
        required
        placeholder="https://www.example.com"
        type="url"
        label={t("Site web (commençant par https://)")}
        {...companyForm.bind("website")}
      />

      <TextInput
        required
        label={t("Numéro de TVA")}
        {...companyForm.bind("vat_number")}
      />

    </Form>
  </>
}

const useCompanyForm = (prefetchedCompany: SearchCompanyPreview) => {
  return useForm({
    activity_description: undefined as string | undefined,
    certificate: undefined as Certificate | undefined,
    entity_type: undefined as EntityType | undefined,
    legal_name: prefetchedCompany?.legal_name as string | undefined,
    name: prefetchedCompany?.legal_name as string | undefined,
    registered_address: prefetchedCompany?.registered_address as string | undefined,
    registered_city: prefetchedCompany?.registered_city as string | undefined,
    registered_country: prefetchedCompany?.registered_country as Country | undefined,
    registered_zipcode: prefetchedCompany?.registered_zipcode as string | undefined,
    registration_id: prefetchedCompany?.registration_id as string | undefined,
    sustainability_officer_email: undefined as string | undefined,
    sustainability_officer_phone_number: undefined as string | undefined,
    sustainability_officer: undefined as string | undefined,
    website: undefined as string | undefined,
    vat_number: undefined as string | undefined,
  } as CompanyRegistrationFormValue)

}

