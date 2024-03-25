import { Certificate, EntityType } from "carbure/types"
import { getEntityTypeLabel, normalizeCertificate } from "carbure/utils/normalizers"
import Autocomplete from "common/components/autocomplete"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import Form, { useForm } from "common/components/form"
import {
  AlertCircle,
  Plus,
  Return
} from "common/components/icons"
import { TextArea, TextInput } from "common/components/input"
import { useNotify, useNotifyError } from "common/components/notifications"
import Portal from "common/components/portal"
import Select from "common/components/select"
import { useMutation } from "common/hooks/async"
import * as api from "companies/api"
import { CreateCompanyFormValue, SearchCompanyPreview } from "companies/types"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import { getCertificates } from "settings/api/certificates"
import { SirenPicker } from "./siren-picker"
import Alert from "common/components/alert"

export const CompanyRegistrationDialog = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()

  const notify = useNotify()
  const notifyError = useNotifyError()
  const [prefetchedCompany, setPrefetchedCompany] = useState<SearchCompanyPreview | undefined>(undefined)
  const [prefetchedCompanyWarning, setPrefetchedCompanyWarning] = useState<string | undefined>(undefined)
  const applyForNewCompanyRequest = useMutation(api.applyForNewCompany, {
    onSuccess: (res) => {
      notify(t("Votre demande d'inscription a bien été envoyéeVotre demande d’inscription de société a bien été prise en compte !"))
      closeDialog()
    },
    onError: (err) => {
      notifyError(err)
    },
  })

  const closeDialog = () => {
    navigate("/account/")
  }

  const fillFormWithfoundCompany = (company: SearchCompanyPreview, warning?: string) => {
    console.log('company:', company)
    setPrefetchedCompany(company)
    if (warning) {
      setPrefetchedCompanyWarning(warning)
    }
    notify(t("Les informations ont été pré-remplies avec les données de l'entreprises"), {
      variant: "success",
    })
  }

  const onSubmitForm = (formValue: CreateCompanyFormValue | undefined) => {
    if (!formValue) return
    applyForNewCompanyRequest.execute(
      formValue.activity_description!,
      formValue.certificate!,
      formValue.entity_type!,
      formValue.legal_name!,
      formValue.registered_address!,
      formValue.registered_city!,
      formValue.registered_country!,
      formValue.registered_zipcode!,
      formValue.registration_id!,
      formValue.sustainability_officer_email!,
      formValue.sustainability_officer_phone_number!,
      formValue.sustainability_officer!,
    )
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
            {prefetchedCompanyWarning &&
              <Alert icon={AlertCircle} variant="warning">
                {prefetchedCompanyWarning}
              </Alert>
            }
            {prefetchedCompany &&
              <PrefetchedCompanyForm prefetchedCompany={prefetchedCompany} onSubmitForm={onSubmitForm} />
            }
          </section>

        </main>

        <footer>

          <Button
            submit="apply-new-company"
            disabled={!prefetchedCompany}
            icon={Plus}
            variant="primary"
            label={t("Demander l'inscription de votre société")}
          />
          <Button icon={Return} asideX action={closeDialog}>
            <Trans>Retour</Trans>
          </Button>

        </footer>

      </Dialog>
    </Portal >
  )
}


interface PrefetchedCompanyFormProps {
  onSubmitForm: (formEntity: CreateCompanyFormValue | undefined) => void
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
      id="apply-new-company"
      onSubmit={onSubmitForm}
    >
      <TextInput
        required
        label={t("N° d'enregistrement de la société (SIREN)")}
        {...companyForm.bind("registration_id")}
      />
      <TextInput
        required
        label={t("Nom légal")}
        {...companyForm.bind("legal_name")}
      />
      <TextInput
        required
        label={t("Adresse de la société (Numéro et rue)")}
        {...companyForm.bind("registered_address")}
      />
      <TextInput
        required
        label={t("Ville")}
        {...companyForm.bind("registered_city")}
      />
      <TextInput
        required
        label={t("Code postal")}
        {...companyForm.bind("registered_zipcode")}
      />
      <TextInput
        readOnly
        required
        label={t("Pays")}
        {...companyForm.bind("registered_country")}
      />
      <TextInput
        required
        label={t("Responsable durabilité")}
        {...companyForm.bind("sustainability_officer")}
      />
      <TextInput
        required
        type="phone"
        label={t("N° téléphone responsable durabilité")}
        {...companyForm.bind("sustainability_officer_phone_number")}
      />
      <TextInput
        required
        type="email"
        label={t("Email responsable durabilité")}
        {...companyForm.bind("sustainability_officer_email")}
      />
      <Autocomplete
        required
        label={t("Certificat (schéma volontaire ou national)")}
        normalize={normalizeCertificate}
        getOptions={(query) =>
          getCertificates(query).then((res) => res.data.data ?? [])
        }
      />

      <Select
        required
        label={t("Type d'activité")}
        placeholder={t("Précisez le type d'activité")}
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
      <TextArea
        required
        label={t("Description de l'activité")}
        {...companyForm.bind("activity_description")}
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
    registered_address: prefetchedCompany?.registered_address as string | undefined,
    registered_city: prefetchedCompany?.registered_city as string | undefined,
    registered_country: prefetchedCompany?.registered_country as string | undefined,
    registered_zipcode: prefetchedCompany?.registered_zipcode as string | undefined,
    registration_id: prefetchedCompany?.registration_id as string | undefined,
    sustainability_officer_email: undefined as string | undefined,
    sustainability_officer_phone_number: undefined as string | undefined,
    sustainability_officer: undefined as string | undefined,
  } as CreateCompanyFormValue)

}

