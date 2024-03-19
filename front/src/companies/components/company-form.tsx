import { Certificate, Entity, EntityType } from "carbure/types"
import { getEntityTypeLabel, normalizeCertificate } from "carbure/utils/normalizers"
import Autocomplete from "common/components/autocomplete"
import Form, { FormManager, useForm } from "common/components/form"
import { TextArea, TextInput } from "common/components/input"
import Select from "common/components/select"
import { useTranslation } from "react-i18next"
import { getCertificates } from "settings/api/certificates"



export interface CompanyFormValue {
  legal_name: string | undefined
  registration_id: string | undefined
  sustainability_officer: string | undefined
  sustainability_officer_phone_number: string | undefined
  sustainability_officer_email: string | undefined
  registered_address: string | undefined
  registered_city: string | undefined
  registered_zipcode: string | undefined
  registered_country: string | undefined
  activity_description: string | undefined
  certificate: Certificate | undefined
  entity_type: EntityType | undefined
}

export interface CreateCompanyFormValue extends CompanyFormValue {
  certificate: Certificate | undefined
  entity_type: EntityType | undefined
}

interface CompanyFormProps {
  form: FormManager<CompanyFormValue | CreateCompanyFormValue>
  entity: Entity
  readOnly?: boolean
  onSubmitForm: (formEntity: CompanyFormValue | CreateCompanyFormValue | undefined) => void
  isNew?: boolean
}

const CompanyForm = ({
  form,
  readOnly = false,
  onSubmitForm,
  isNew = false,
}: CompanyFormProps) => {

  const { t } = useTranslation()

  return <>
    <Form
      form={form}
      id="entity-info"
      onSubmit={onSubmitForm}
    >
      <TextInput
        readOnly={readOnly}
        label={t("N° d'enregistrement de la société (SIREN)")}
        {...form.bind("registration_id")}
      />
      <TextInput
        readOnly={readOnly}
        label={t("Nom légal")}
        {...form.bind("legal_name")}
      />
      <TextInput
        readOnly={readOnly}
        label={t("Adresse de la société (Numéro et rue)")}
        {...form.bind("registered_address")}
      />
      <TextInput
        readOnly={readOnly}
        label={t("Ville")}
        {...form.bind("registered_city")}
      />
      <TextInput
        readOnly={readOnly}
        label={t("Code postal")}
        {...form.bind("registered_zipcode")}
      />
      <TextInput
        readOnly={readOnly}
        label={t("Pays")}
        {...form.bind("registered_country")}
      />
      <TextInput
        readOnly={readOnly}
        label={t("Responsable durabilité")}
        {...form.bind("sustainability_officer")}
      />
      <TextInput
        type="phone"
        readOnly={readOnly}
        label={t("N° téléphone responsable durabilité")}
        {...form.bind("sustainability_officer_phone_number")}
      />
      <TextInput
        type="email"
        readOnly={readOnly}
        label={t("Email responsable durabilité")}
        {...form.bind("sustainability_officer_email")}
      />
      {isNew &&
        <Autocomplete
          autoFocus
          readOnly={readOnly}
          label={t("Certificat (schéma volontaire ou national)")}
          normalize={normalizeCertificate}
          getOptions={(query) =>
            getCertificates(query).then((res) => res.data.data ?? [])
          }
          {...form.bind("certificate")}
        />}
      {isNew &&
        <Select
          readOnly={readOnly}
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
        />}
      <TextArea
        readOnly={readOnly}
        label={t("Description de l'activité")}
        {...form.bind("activity_description")}
      />
    </Form>
  </>
}

export const useCompanyForm = (entity: Entity) => {
  return useForm({
    certificate: undefined as Certificate | undefined,
    activity_description: entity.activity_description as string | undefined,
    entity_type: entity.entity_type as EntityType | undefined,
    legal_name: entity.legal_name as string | undefined,
    registered_address: entity.registered_address as string | undefined,
    registered_city: entity.registered_city as string | undefined,
    registered_country: entity.registered_country as string | undefined,
    registered_zipcode: entity.registered_zipcode as string | undefined,
    registration_id: entity.registration_id as string | undefined,
    sustainability_officer_email: entity.sustainability_officer_email as string | undefined,
    sustainability_officer_phone_number: entity.sustainability_officer_phone_number as string | undefined,
    sustainability_officer: entity.sustainability_officer as string | undefined,

  })

}


export default CompanyForm