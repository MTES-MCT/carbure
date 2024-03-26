import useEntity from "carbure/hooks/entity"
import { Country, Entity, UserRole } from "carbure/types"
import Button from "common/components/button"
import Form, { useForm } from "common/components/form"
import { Save } from "common/components/icons"
import { TextArea, TextInput } from "common/components/input"
import { LoaderOverlay, Panel } from "common/components/scaffold"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import * as api from "../api/company"
import { CompanyFormValue } from "companies/types"
import Autocomplete from "common/components/autocomplete"
import { findCountries } from "carbure/api"
import { normalizeCountry } from "carbure/utils/normalizers"


type CompanyInfoProps = {
  company?: Entity
}

const CompanyInfo = ({ company }: CompanyInfoProps) => {
  const { t } = useTranslation()
  const loggedEntity = useEntity()

  const entity = company || loggedEntity
  const readOnly = company && !loggedEntity.hasRights(UserRole.Admin, UserRole.ReadWrite)

  const updateEntity = useMutation(api.updateEntity, {
    invalidates: ["user-settings"],
  })
  const companyForm = useCompanyForm(entity)

  const canSave = hasChange(entity, companyForm.value)

  const onSubmitForm = (formValue: CompanyFormValue | undefined) => {
    if (formValue && canSave) {
      updateEntity.execute(
        entity.id,
        formValue.activity_description!,
        formValue.legal_name!,
        formValue.registered_address!,
        formValue.registered_city!,
        formValue.registered_country?.code_pays!,
        formValue.registered_zipcode!,
        formValue.registration_id!,
        formValue.sustainability_officer_email!,
        formValue.sustainability_officer_phone_number!,
        formValue.sustainability_officer!,
      )
    }
  }


  return (
    <Panel id="info">
      <header>
        <h1>{t("Informations sur la société")}</h1>
        {!readOnly && (
          <Button
            asideX
            submit="entity-info"
            disabled={!canSave}
            icon={Save}
            variant="primary"
            label={t("Enregistrer les modifications")}
          />
        )}
      </header>

      {!readOnly && (
        <section>
          <p>
            {t(
              "Veuillez renseigner les informations de contact de votre société."
            )}
          </p>
        </section>
      )}

      <section>
        <Form
          form={companyForm}
          id="entity-info"
          onSubmit={onSubmitForm}
        >
          <TextInput
            readOnly={readOnly}
            label={t("N° d'enregistrement de la société (SIREN)")}
            {...companyForm.bind("registration_id")}
          />
          <TextInput
            readOnly={readOnly}
            label={t("Nom légal")}
            {...companyForm.bind("legal_name")}
          />
          <TextInput
            readOnly={readOnly}
            label={t("Adresse de la société (Numéro et rue)")}
            {...companyForm.bind("registered_address")}
          />
          <TextInput
            readOnly={readOnly}
            label={t("Ville")}
            {...companyForm.bind("registered_city")}
          />
          <TextInput
            readOnly={readOnly}
            label={t("Code postal")}
            {...companyForm.bind("registered_zipcode")}
          />
          <Autocomplete
            readOnly={readOnly}
            label={t("Pays")}
            placeholder={t("Rechercher un pays...")}
            getOptions={findCountries}
            normalize={normalizeCountry}
            {...companyForm.bind("registered_country")}
          />
          <TextInput
            readOnly={readOnly}
            label={t("Responsable durabilité")}
            {...companyForm.bind("sustainability_officer")}
          />
          <TextInput
            type="phone"
            readOnly={readOnly}
            label={t("N° téléphone responsable durabilité")}
            {...companyForm.bind("sustainability_officer_phone_number")}
          />
          <TextInput
            type="email"
            readOnly={readOnly}
            label={t("Email responsable durabilité")}
            {...companyForm.bind("sustainability_officer_email")}
          />

          <TextArea
            readOnly={readOnly}
            label={t("Description de l'activité")}
            {...companyForm.bind("activity_description")}
          />
        </Form>
      </section>

      <footer />

      {updateEntity.loading && <LoaderOverlay />}
    </Panel>
  )
}


export default CompanyInfo


function hasChange(entity: Entity, formEntity: CompanyFormValue) {
  return (
    entity.legal_name !== formEntity.legal_name ||
    entity.registration_id !== formEntity.registration_id ||
    entity.sustainability_officer !== formEntity.sustainability_officer ||
    entity.sustainability_officer_phone_number !== formEntity.sustainability_officer_phone_number ||
    entity.sustainability_officer_email !== formEntity.sustainability_officer_email ||
    entity.registered_address !== formEntity.registered_address ||
    entity.registered_city !== formEntity.registered_city ||
    entity.registered_zipcode !== formEntity.registered_zipcode ||
    entity.registered_country !== formEntity.registered_country ||
    entity.activity_description !== formEntity.activity_description
  )
}


const useCompanyForm = (entity: Entity) => {
  return useForm({
    activity_description: entity?.activity_description as string | undefined,
    legal_name: entity?.legal_name as string | undefined,
    registered_address: entity?.registered_address as string | undefined,
    registered_city: entity?.registered_city as string | undefined,
    registered_country: entity?.registered_country as Country | undefined,
    registered_zipcode: entity?.registered_zipcode as string | undefined,
    registration_id: entity?.registration_id as string | undefined,
    sustainability_officer_email: entity?.sustainability_officer_email as string | undefined,
    sustainability_officer_phone_number: entity?.sustainability_officer_phone_number as string | undefined,
    sustainability_officer: entity?.sustainability_officer as string | undefined,
  })
}
