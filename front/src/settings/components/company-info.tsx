import { useTranslation } from "react-i18next"
import useEntity from "carbure/hooks/entity"
import { Entity, UserRole } from "carbure/types"
import { useMutation } from "common/hooks/async"
import { Panel, LoaderOverlay } from "common/components/scaffold"
import * as api from "../api/company"
import Form, { FormManager, useForm } from "common/components/form"
import { TextInput } from "common/components/input"
import Button from "common/components/button"
import { Save } from "common/components/icons"
import { useEffect } from "react"
import CompanyForm, { CompanyFormValue, CreateCompanyFormValue, useCompanyForm } from "companies/components/company-form"

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

  const onSubmitForm = (formValue: CompanyFormValue | CreateCompanyFormValue | undefined) => {
    if (formValue && canSave) {
      updateEntity.execute(
        entity.id,
        formValue.activity_description!,
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
        <CompanyForm form={companyForm} readOnly={readOnly} onSubmitForm={onSubmitForm} />
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
    undefined !== formEntity.certificate ||
    entity.entity_type !== formEntity.entity_type ||
    entity.activity_description !== formEntity.activity_description
  )
}

