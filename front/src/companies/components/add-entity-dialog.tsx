import { AxiosError } from "axios"
import useEntity from "carbure/hooks/entity"
import { EntityType } from "carbure/types"
import * as norm from "carbure/utils/normalizers"
import Autocomplete from "common/components/autocomplete"
import Button from "common/components/button"
import Checkbox from "common/components/checkbox"
import Dialog from "common/components/dialog"
import Form, { useForm } from "common/components/form"
import { Return, Send } from "common/components/icons"
import { TextInput } from "common/components/input"
import Portal from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import * as api from "../api"

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
  const hasAirlineOnly = entity.isExternal && entity.hasAdminRight("AIRLINE")

  const { value, bind } = useForm<AddForm>(defaultEntity)

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
      value.has_elec
    )
    onEntityAdded(value.name!)
    onClose()
  }

  return (
    <Portal onClose={onClose}>
      <Dialog onClose={onClose}>
        <header>
          <h1>{t("Ajouter une société")}</h1>
        </header>

        <main>
          <section>
            <Form id="add-entity" onSubmit={addEntity}>
              <TextInput required label={t("Nom")} {...bind("name")} />

              <Autocomplete
                required
                label={t("Type de société")}
                normalize={norm.normalizeEntityType}
                options={
                  hasAirlineOnly
                    ? [EntityType.Airline]
                    : [
                        EntityType.Operator,
                        EntityType.Producer,
                        EntityType.Trader,
                        EntityType.Auditor,
                        EntityType.Airline,
                        EntityType.ExternalAdmin,
                      ]
                }
                {...bind("entity_type")}
              />

              {value.entity_type === EntityType.Operator && (
                <Checkbox
                  label={t(
                    "Ajouter la gestion du Carburant Durable d’Aviation"
                  )}
                  {...bind("has_saf")}
                />
              )}

              {value.entity_type === EntityType.Operator && (
                <Checkbox
                  label={t(
                    "Ajouter la gestion de la cession d'Energie Electrique"
                  )}
                  {...bind("has_elec")}
                />
              )}
            </Form>
          </section>
        </main>

        <footer>
          <Button
            icon={Send}
            label={t("Ajouter")}
            variant="primary"
            submit="add-entity"
            disabled={addEntityRequest.loading}
          />

          <Button icon={Return} label={t("Retour")} action={onClose} />
        </footer>
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
}

export type AddForm = typeof defaultEntity
