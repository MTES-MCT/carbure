import { AxiosError } from "axios"
import useEntity from "common/hooks/entity"
import { EntityType, ExternalAdminPages } from "common/types"
import * as norm from "common/utils/normalizers"
import { Autocomplete } from "common/components/autocomplete2"
import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { Form, useForm } from "common/components/form2"
import { TextInput, Checkbox } from "common/components/inputs2"
import Portal from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import * as api from "../api"
import { SiretPicker } from "common/molecules/siret-picker"
import { AutoCompleteDepartments } from "common/molecules/autocomplete-departments"
import { useCompanyTypesByEntity } from "companies-admin/hooks/useCompanyTypesByEntity"

export interface AddEntityDialogProps {
  onClose: () => void
  onEntityAdded: (entityName: string) => void
}

export const AddEntityDialog = ({
  onClose,
  onEntityAdded,
}: AddEntityDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const companyTypes = useCompanyTypesByEntity()
  const { value, bind, setField } = useForm<AddForm>({
    ...defaultEntity,
    entity_type:
      companyTypes.length === 1 ? companyTypes[0] : defaultEntity.entity_type,
  })

  const addEntityRequest = useMutation(api.addCompany, {
    invalidates: ["entities"],
    onError: (err) => {
      const error = (err as AxiosError<{ error: string }>).response?.data.error
      if (error === "ENTITY_EXISTS") {
        alert("La société existe déjà")
      }
    },
  })

  const addEntity = async () => {
    await addEntityRequest.execute(
      entity.id,
      value.name!,
      value.entity_type!,
      value.has_saf,
      value.has_elec,
      value.company_address!,
      value.postal_code!,
      value.city!,
      value.department!,
      value.insee_code!
    )
    onEntityAdded(value.name!)
    onClose()
  }
  const canAddCompany =
    (entity.hasAdminRight(ExternalAdminPages.DREAL) && value.company_address) ||
    !entity.hasAdminRight(ExternalAdminPages.DREAL)

  return (
    <Portal onClose={onClose}>
      <Dialog
        onClose={onClose}
        header={<Dialog.Title>{t("Ajouter une société")}</Dialog.Title>}
        footer={
          <Button
            iconId="ri-send-plane-line"
            nativeButtonProps={{
              form: "add-entity",
            }}
            loading={addEntityRequest.loading}
            disabled={!canAddCompany || addEntityRequest.loading}
            type="submit"
          >
            {t("Ajouter")}
          </Button>
        }
      >
        <Form id="add-entity" onSubmit={addEntity}>
          <TextInput required label={t("Nom")} {...bind("name")} />
          <Autocomplete
            required
            label={t("Type de société")}
            normalize={norm.normalizeEntityType}
            options={companyTypes}
            {...bind("entity_type")}
          />
          <SiretPicker
            {...bind("siret")}
            required
            label={t("Siret de la société")}
            onSelect={(company) => {
              if (company) {
                setField("company_address", company?.registered_address)
                setField("postal_code", company?.registered_zipcode)
                setField("city", company?.registered_city)
                setField("department", company?.department_code)
                setField("insee_code", company?.insee_code)
              }
            }}
          />
          {value.company_address && (
            <>
              <TextInput
                required
                label={t("Adresse de la société (Numéro et rue)")}
                {...bind("company_address")}
              />
              <TextInput
                required
                label={t("Code postal")}
                {...bind("postal_code")}
              />
              <TextInput required label={t("Ville")} {...bind("city")} />
              <AutoCompleteDepartments
                required
                label={t("Département")}
                {...bind("department")}
                onChange={(value) => {
                  setField("department", value ?? undefined)
                }}
              />
              <TextInput
                required
                label={t("Code INSEE")}
                {...bind("insee_code")}
              />
            </>
          )}

          {value.entity_type === EntityType.Operator && (
            <Checkbox
              label={t("Ajouter la gestion du Carburant Durable d'Aviation")}
              {...bind("has_saf")}
            />
          )}

          {value.entity_type === EntityType.Operator && (
            <Checkbox
              label={t("Ajouter la gestion de la cession d'Energie Electrique")}
              {...bind("has_elec")}
            />
          )}
        </Form>
      </Dialog>
    </Portal>
  )
}

export default AddEntityDialog

const defaultEntity = {
  name: "" as string | undefined,
  entity_type: EntityType.Unknown as EntityType | undefined,
  has_saf: false as boolean,
  has_elec: false as boolean,
  siret: "" as string | undefined,
  company_address: "" as string | undefined,
  postal_code: "" as string | undefined,
  city: "" as string | undefined,
  department: "" as string | undefined,
  insee_code: "" as string | undefined,
}

export type AddForm = typeof defaultEntity
