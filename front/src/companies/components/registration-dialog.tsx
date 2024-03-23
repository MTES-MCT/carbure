import { Certificate, EntityType } from "carbure/types"
import { getEntityTypeLabel, normalizeCertificate } from "carbure/utils/normalizers"
import Autocomplete from "common/components/autocomplete"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import Form, { useForm } from "common/components/form"
import {
  Plus,
  Return
} from "common/components/icons"
import { TextArea, TextInput } from "common/components/input"
import { useNotify, useNotifyError } from "common/components/notifications"
import Portal from "common/components/portal"
import Select from "common/components/select"
import { useMutation } from "common/hooks/async"
import * as api from "companies/api"
import { CreateCompanyFormValue, SearchCompanyResult } from "companies/types"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import { getCertificates } from "settings/api/certificates"
import { SirenPicker } from "./siren-picker"

export const CompanyRegistrationDialog = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const [prefetchedCompany, setPrefetchedCompany] = useState<SearchCompanyResult | undefined>(undefined)



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

  const fillFormWithfoundCompany = (company: SearchCompanyResult) => {
    setPrefetchedCompany(company)
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
            {prefetchedCompany &&
              <PrefetchedCompanyForm prefetchedCompany={prefetchedCompany} onSubmitForm={onSubmitForm} />
            }
          </section>

        </main>

        <footer>

          <Button
            submit="apply-new-company"
            // disabled={!canSave}
            icon={Plus}
            variant="primary"
            label={t("Demander l’inscription de votre société")}
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
  prefetchedCompany: SearchCompanyResult
}

const PrefetchedCompanyForm = ({
  onSubmitForm,
  prefetchedCompany
}: PrefetchedCompanyFormProps) => {
  const { t } = useTranslation()

  const companyForm = useForm({
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
        label={t("Pays")}
        {...companyForm.bind("registered_country")}
      />
      <TextInput
        label={t("Responsable durabilité")}
        {...companyForm.bind("sustainability_officer")}
      />
      <TextInput
        type="phone"
        label={t("N° téléphone responsable durabilité")}
        {...companyForm.bind("sustainability_officer_phone_number")}
      />
      <TextInput
        type="email"
        label={t("Email responsable durabilité")}
        {...companyForm.bind("sustainability_officer_email")}
      />
      <Autocomplete
        label={t("Certificat (schéma volontaire ou national)")}
        normalize={normalizeCertificate}
        getOptions={(query) =>
          getCertificates(query).then((res) => res.data.data ?? [])
        }
      />

      <Select
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



