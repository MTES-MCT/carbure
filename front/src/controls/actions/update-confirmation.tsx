import { Entity } from "carbure/types"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import Form from "common/components/form"
import { Edit, Return } from "common/components/icons"
import { TextInput } from "common/components/input"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Lot } from "transactions/types"
import * as api from "../api/admin"

interface UpdateConfirmationDialogProps {
  onClose: () => void
  lots: Lot[]
  value: string
}
const UpdateConfirmationDialog = ({
  onClose,
  lots,
  value,
}: UpdateConfirmationDialogProps) => {
  const { t } = useTranslation()
  const [comment, setComment] = useState<string | undefined>()
  const notify = useNotify()

  const updateLots = useMutation(api.updateLots, {
    invalidates: [
      "ticket-source-details",
      "tickets",
      "operator-snapshot",
      "ticket-sources",
    ],
    onSuccess: () => {
      notify(
        t("Les {lotCount} lots sélectionnés ont été modifiés", {
          lotCount: lots.length,
        }),
        { variant: "success" }
      )
      onClose()
    },
    onError: () => {
      //TODO display errors
    },
  })

  const entities_to_notify: Entity[] = []
  const lots_ids: number[] = []
  lots.forEach((lot) => {
    lots_ids.push(lot.id)
    if (lot.carbure_client) {
      entities_to_notify.push(lot.carbure_client)
    }
  })
  const entities_names = entities_to_notify.map((e) => e.name).join(", ")

  const submit = () => {
    const entities_ids_to_notify = entities_to_notify.map((e) => e.id)
    return updateLots.execute(lots_ids, value, entities_ids_to_notify)
  }
  const editLots = async () => {}

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>
          {t("{{lotCount}} lots vont être modifiés", {
            lotCount: lots.length,
          })}
        </h1>
      </header>
      <main>
        <section>
          <p>
            <strong>
              {t(
                "Êtes-vous sûr de vouloir modifier l’integralité de ces lots ?"
              )}
            </strong>
            {t(
              "Une notification sera envoyée aux sociétés concernées avec votre commentaire."
            )}
          </p>
          <Form id="edit-lots" onSubmit={editLots}>
            <TextInput
              value={comment}
              label={t("Commentaire")}
              onChange={setComment}
              required
              placeholder={t("Entrez un commentaire...")}
            />
          </Form>
          <p>
            Info modifiée : <strong>{value}</strong>
          </p>
          <p>
            Sociétés concernées : <strong>{entities_names}</strong>
          </p>
        </section>
      </main>

      <footer>
        <Button variant="warning" icon={Edit} action={submit}>
          {t("Modifier les 15 lots")}
        </Button>

        <Button icon={Return} action={onClose}>
          {t("Annuler")}
        </Button>
      </footer>
    </Dialog>
  )
}

export default UpdateConfirmationDialog
