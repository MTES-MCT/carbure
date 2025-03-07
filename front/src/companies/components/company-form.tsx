import { findCountries } from "common/api"
import { Certificate, Country, EntityType } from "common/types"
import {
  getEntityTypeLabel,
  normalizeCertificate,
  normalizeCountry,
} from "common/utils/normalizers"
import Autocomplete from "common/components/autocomplete"
import { useForm, Form } from "common/components/form"
import { TextArea, TextInput } from "common/components/input"
import Select from "common/components/select"
import {
  CompanyRegistrationFormValue,
  SearchCompanyPreview,
} from "companies/types"
import { useTranslation } from "react-i18next"
import { getCertificates } from "settings/api/certificates"

interface CompanyFormProps {
  onSubmitForm: (formEntity: CompanyRegistrationFormValue | undefined) => void
  company?: SearchCompanyPreview
  isForeignCompany?: boolean
  formId?: string
}
export const CompanyForm = ({
  onSubmitForm,
  company,
  isForeignCompany = false,
  formId = "add-company",
}: CompanyFormProps) => {
  const { t } = useTranslation()
  const companyForm = useCompanyForm(company)

  return (
    <Form form={companyForm} id={formId} onSubmit={onSubmitForm}>
      {!isForeignCompany && (
        <TextInput
          required
          label={t("N° d'enregistrement de la société (SIREN)")}
          {...companyForm.bind("registration_id")}
          disabled
        />
      )}

      <TextInput
        required
        label={t("Nom de la société (visible dans carbure)")}
        {...companyForm.bind("name")}
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
      <Autocomplete
        label={t("Pays")}
        placeholder={t("Rechercher un pays...")}
        getOptions={(query) => findCountries(query, { exclude_france: true })}
        normalize={normalizeCountry}
        {...companyForm.bind("registered_country")}
        required={isForeignCompany}
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
        label={t(
          "N° téléphone responsable durabilité (commence par +33 pour la France)"
        )}
        placeholder="exemple : +33612345678"
        {...companyForm.bind("sustainability_officer_phone_number")}
      />
      <TextInput
        required
        type="email"
        label={t("Email de contact")}
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
            value: EntityType.Auditor,
            label: getEntityTypeLabel(EntityType.Auditor),
          },
          {
            value: EntityType.PowerOrHeatProducer,
            label: getEntityTypeLabel(EntityType.PowerOrHeatProducer),
          },
        ]}
      />
      {companyForm.value?.entity_type &&
        ![EntityType.Airline, EntityType.CPO].includes(
          companyForm.value?.entity_type
        ) && (
          <Autocomplete
            label={t("Certificat (schéma volontaire ou national)")}
            normalize={normalizeCertificate}
            getOptions={(query) =>
              getCertificates(query).then((res) => res.data ?? [])
            }
            {...companyForm.bind("certificate")}
          />
        )}
      <TextArea
        required
        label={t("Description de l'activité")}
        maxLength={5000}
        {...companyForm.bind("activity_description")}
      />

      <TextInput
        placeholder="https://www.example.com"
        type="url"
        label={t("Site web (commençant par https://)")}
        {...companyForm.bind("website")}
      />

      <TextInput
        label={t("Numéro de TVA")}
        {...companyForm.bind("vat_number")}
      />
    </Form>
  )
}

const useCompanyForm = (prefetchedCompany?: SearchCompanyPreview) => {
  return useForm({
    activity_description: undefined as string | undefined,
    certificate: undefined as Certificate | undefined,
    entity_type: undefined as EntityType | undefined,
    legal_name: prefetchedCompany?.legal_name as string | undefined,
    name: prefetchedCompany?.legal_name as string | undefined,
    registered_address: prefetchedCompany?.registered_address as
      | string
      | undefined,
    registered_city: prefetchedCompany?.registered_city as string | undefined,
    registered_country: prefetchedCompany?.registered_country as
      | Country
      | undefined,
    registered_zipcode: prefetchedCompany?.registered_zipcode as
      | string
      | undefined,
    registration_id: prefetchedCompany?.registration_id as string | undefined,
    sustainability_officer_email: undefined as string | undefined,
    sustainability_officer_phone_number: undefined as string | undefined,
    sustainability_officer: undefined as string | undefined,
    website: undefined as string | undefined,
    vat_number: undefined as string | undefined,
  } as CompanyRegistrationFormValue)
}
