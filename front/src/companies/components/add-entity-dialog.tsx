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

  const { value, bind } = useForm<AddForm>(defaultEntity)

  const closeDialog = () => {
    onClose()
  }

  const addEntityRequest = useMutation(api.addEntity, {
    invalidates: ["entities"],
  })

  const addEntity = async () => {
    // TO TEST uncomment below
    // await addEntityRequest.execute(value.name, value.entity_type, value.has_saf)
    onEntityAdded(value.name!)
    onClose()
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog}>
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
                options={[
                  EntityType.Operator,
                  EntityType.Producer,
                  EntityType.Trader,
                  EntityType.Auditor,
                ]}
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
            </Form>
          </section>
        </main>

        <footer>
          <Button
            icon={Send}
            label={t("Ajouter")}
            variant="primary"
            submit="add-entity"
          />

          <Button icon={Return} label={t("Retour")} action={closeDialog} />
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
}

export type AddForm = typeof defaultEntity
