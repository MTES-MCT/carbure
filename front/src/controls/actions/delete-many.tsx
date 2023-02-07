import { AxiosError } from "axios"
import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import Form from "common/components/form"
import { Cross, Edit, Return } from "common/components/icons"
import { TextInput } from "common/components/input"
import { useNotify } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { LotsUpdateError, LotsUpdateResponse } from "controls/types"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Lot } from "transactions/types"
import * as api from "../api/admin"
import { getLotsEntitiesToNotify } from "./update-many-confirmation"
import { UpdateErrorsDialog } from "./update-many-errors"

export interface DeleteManyButtonProps {
  disabled?: boolean
  selection: number[]
  lots: Lot[]
}

export const DeleteManyButton = ({
  disabled,
  selection,
  lots,
}: DeleteManyButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      disabled={disabled || selection.length === 0}
      variant="danger"
      icon={Cross}
      label={t("Supprimer la séléction")}
      action={() =>
        portal((close) => (
          <DeleteManyConfirmationDialog onClose={close} lots={lots} />
        ))
      }
    />
  )
}

interface DeleteManyConfirmationDialogProps {
  onClose: () => void
  lots: Lot[]
}
const DeleteManyConfirmationDialog = ({
  onClose,
  lots,
}: DeleteManyConfirmationDialogProps) => {
  const { t } = useTranslation()
  const [comment, setComment] = useState<string | undefined>()
  const entity = useEntity()
  const notify = useNotify()
  const portal = usePortal()
  const deleteLots = useMutation(api.deleteLots, {
    invalidates: ["controls"],
    onSuccess: () => {
      notify(
        t("Les {{count}} lots sélectionnés ont bien été supprimés.", {
          count: lots.length,
        }),
        { variant: "success" }
      )
      onClose()
    },
    onError: (err) => {
      const errors = (err as AxiosError<LotsUpdateResponse>).response?.data
        .errors
      errors && showErrors(errors!)
    },
  })

  const entities_to_notify: string = getLotsEntitiesToNotify(lots)
  const showErrors = (errors: LotsUpdateError[]) => {
    portal((close) => (
      <UpdateErrorsDialog onClose={close} errors={errors} method="delete" />
    ))
  }

  const submit = () => {
    return deleteLots.execute(
      entity.id,
      lots.map((l) => l.id),
      comment!
    )
    //TOTEST uncomment below
    // showErrors(lotsUpdateErrorsResponse.errors!)
  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>
          {t("{{count}} lots vont être supprimés.", {
            count: lots.length,
          })}
        </h1>
      </header>
      <main>
        <section>
          <p>
            <strong>
              {t(
                "Êtes-vous sûr de vouloir supprimer l’integralité de ces lots ?"
              )}
            </strong>{" "}
            {t(
              "Une notification sera envoyé aux sociétés concernées (sans le commentaire)."
            )}
          </p>
          <Form id="delete-lots" onSubmit={submit}>
            <TextInput
              value={comment}
              label={t("Commentaire interne")}
              onChange={setComment}
              required
              placeholder={t("Entrez un commentaire...")}
            />
          </Form>
          <p>
            {t("Sociétés concernées")} : <strong>{entities_to_notify}</strong>
          </p>
        </section>
      </main>

      <footer>
        <Button variant="warning" icon={Edit} submit="delete-lots">
          {t("Supprimer les {{count}} lots", {
            count: lots.length,
          })}
        </Button>

        <Button icon={Return} action={onClose}>
          {t("Annuler")}
        </Button>
      </footer>
    </Dialog>
  )
}
