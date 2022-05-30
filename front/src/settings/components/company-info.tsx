import { useTranslation } from "react-i18next"
import useEntity from "carbure/hooks/entity"
import { Entity, UserRole } from "carbure/types"
import { useMutation } from "common-v2/hooks/async"
import { Panel, LoaderOverlay } from "common-v2/components/scaffold"
import * as api from "../api-v2"
import Form, { useForm } from "common-v2/components/form"
import { TextInput } from "common-v2/components/input"
import Button from "common-v2/components/button"
import { Save } from "common-v2/components/icons"

const CompanyInfo = () => {
  const { t } = useTranslation()
  const entity = useEntity()

  const canModify = entity.hasRights(UserRole.Admin, UserRole.ReadWrite)

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
  })

  const canSave = hasChange(entity, formEntity)

  return (
    <Panel id="info">
      <header>
        <h1>{t("Informations sur la société")}</h1>
        <Button
          asideX
          submit="entity-info"
          disabled={!canSave}
          icon={Save}
          variant="primary"
          label={t("Enregistrer les modifications")}
        />
      </header>

      <section>
        <Form
          id="entity-info"
          onSubmit={() => {
            if (canSave) {
              updateEntity.execute(
                entity.id,
                formEntity.legal_name!,
                formEntity.registration_id!,
                formEntity.registered_address!,
                formEntity.sustainability_officer!,
                formEntity.sustainability_officer_phone_number!
              )
            }
          }}
        >
          <TextInput
            disabled={!canModify}
            label={t("Nom légal")}
            {...bind("legal_name")}
          />
          <TextInput
            disabled={!canModify}
            label={t("N° d'enregistrement de la société")}
            {...bind("registration_id")}
          />
          <TextInput
            disabled={!canModify}
            label={t("Addresse de la société")}
            {...bind("registered_address")}
          />
          <TextInput
            disabled={!canModify}
            label={t("Responsable durabilité")}
            {...bind("sustainability_officer")}
          />
          <TextInput
            type="phone"
            disabled={!canModify}
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
    entity.registered_address !== formEntity.registered_address
  )
}

export default CompanyInfo
