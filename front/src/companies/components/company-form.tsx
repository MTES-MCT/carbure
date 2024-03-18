import { useTranslation } from "react-i18next"
import useEntity from "carbure/hooks/entity"
import { Entity, UserRole } from "carbure/types"
import { useMutation } from "common/hooks/async"
import { Panel, LoaderOverlay } from "common/components/scaffold"
import Form, { FormManager, useForm } from "common/components/form"
import { TextInput } from "common/components/input"
import Button from "common/components/button"
import { Save } from "common/components/icons"
import { useEffect } from "react"



export type CompanyFormValue = {
  legal_name: string | undefined
  registration_id: string | undefined
  sustainability_officer: string | undefined
  sustainability_officer_phone_number: string | undefined
  registered_address: string | undefined
  registered_city: string | undefined
  registered_zipcode: string | undefined
  registered_country: string | undefined
}
interface CompanyFormProps {
  form: FormManager<CompanyFormValue>
  entity: Entity
  readOnly?: boolean
  onSubmitForm: (formEntity: CompanyFormValue | undefined) => void
}

const CompanyForm = ({
  form,
  readOnly = false,
  onSubmitForm
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
        label={t("Nom légal")}
        {...form.bind("legal_name")}
      />
      <TextInput
        readOnly={readOnly}
        label={t("N° d'enregistrement de la société")}
        {...form.bind("registration_id")}
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
    </Form>
  </>
}

export const useCompanyForm = (entity: Entity) => {
  return useForm({
    legal_name: entity.legal_name as string | undefined,
    registration_id: entity.registration_id as string | undefined,
    sustainability_officer_phone_number:
      entity.sustainability_officer_phone_number as string | undefined,
    sustainability_officer: entity.sustainability_officer as string | undefined,
    registered_address: entity.registered_address as string | undefined,
    registered_city: entity.registered_city as string | undefined,
    registered_zipcode: entity.registered_zipcode as string | undefined,
    registered_country: entity.registered_country as string | undefined,
  })

}


export default CompanyForm