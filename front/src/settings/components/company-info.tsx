import { useTranslation } from "react-i18next"
import useEntity from "carbure/hooks/entity"
import { Entity, UserRole } from "carbure/types"
import { useMutation } from "common/hooks/async"
import { Panel, LoaderOverlay } from "common/components/scaffold"
import * as api from "../api/company"
import Form, { useForm } from "common/components/form"
import { TextInput } from "common/components/input"
import Button from "common/components/button"
import { Save } from "common/components/icons"
import { useEffect } from "react"

type CompanyInfoProps = {
  company?: Entity
}

const CompanyInfo = ({ company }: CompanyInfoProps) => {
  const { t } = useTranslation()
  const loggedEntity = useEntity()

  const entity = company || loggedEntity
  const canModify = !company && loggedEntity.hasRights(UserRole.Admin, UserRole.ReadWrite)



  const updateEntity = useMutation(api.updateEntity, {
    invalidates: ["user-settings"],
  })



  const { bind, value: formEntity } = useForm({
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

  const canSave = hasChange(entity, formEntity)

  const onSubmitForm = () => {
    if (canSave) {
      updateEntity.execute(
        entity.id,
        formEntity.legal_name!,
        formEntity.registration_id!,
        formEntity.registered_address!,
        formEntity.registered_zipcode!,
        formEntity.registered_city!,
        formEntity.registered_country!,
        formEntity.sustainability_officer!,
        formEntity.sustainability_officer_phone_number!
      )
    }
  }


  return (
    <Panel id="info">
      <header>
        <h1>{t("Informations sur la société")}</h1>
        {canModify && (
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

      {canModify && (
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
          id="entity-info"
          onSubmit={onSubmitForm}
        >
          <TextInput
            readOnly={!canModify}
            label={t("Nom légal")}
            {...bind("legal_name")}
          />
          <TextInput
            readOnly={!canModify}
            label={t("N° d'enregistrement de la société")}
            {...bind("registration_id")}
          />
          <TextInput
            readOnly={!canModify}
            label={t("Adresse de la société (Numéro et rue)")}
            {...bind("registered_address")}
          />
          <TextInput
            readOnly={!canModify}
            label={t("Ville")}
            {...bind("registered_city")}
          />
          <TextInput
            readOnly={!canModify}
            label={t("Code postal")}
            {...bind("registered_zipcode")}
          />
          <TextInput
            readOnly={!canModify}
            label={t("Pays")}
            {...bind("registered_country")}
          />
          <TextInput
            readOnly={!canModify}
            label={t("Responsable durabilité")}
            {...bind("sustainability_officer")}
          />
          <TextInput
            type="phone"
            readOnly={!canModify}
            label={t("N° téléphone responsable durabilité")}
            {...bind("sustainability_officer_phone_number")}
          />
        </Form>
      </section>

      <footer />

      {updateEntity.loading && <LoaderOverlay />}
    </Panel>
  )
}

function hasChange(entity: Partial<Entity>, formEntity: Partial<Entity>) {
  return (
    entity.legal_name !== formEntity.legal_name ||
    entity.registration_id !== formEntity.registration_id ||
    entity.sustainability_officer !== formEntity.sustainability_officer ||
    entity.sustainability_officer_phone_number !==
    formEntity.sustainability_officer_phone_number ||
    entity.registered_address !== formEntity.registered_address ||
    entity.registered_city !== formEntity.registered_city ||
    entity.registered_zipcode !== formEntity.registered_zipcode ||
    entity.registered_country !== formEntity.registered_country
  )
}

export default CompanyInfo
