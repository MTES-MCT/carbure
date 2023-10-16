import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import Form from "common/components/form"
import { AlertCircle, Cross, Edit, Return } from "common/components/icons"
import { TextInput } from "common/components/input"
import { useNotify } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { useMutation, useQuery } from "common/hooks/async"
import { useMemo, useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { Lot } from "transactions/types"
import * as api from "../api/admin"
import { getLotsEntitiesToNotify } from "./update-many-confirmation"

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

  const lots_ids = useMemo(() => lots.map((l) => l.id), [lots])

  const requestedDeletions = useQuery(api.deleteLots, {
    key: "check-updates",
    params: [entity.id, lots_ids, "check", true],
  })

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
  })

  const entities_to_notify: string = getLotsEntitiesToNotify(lots)
  // const showErrors = (errors: LotsUpdateErrors) => { //TODO si pas d'erreur possible, supprimer ce code
  //   portal((close) => (
  //     <UpdateErrorsDialog onClose={close} errors={errors} method="delete" />
  //   ))
  // }

  const submit = () => {
    return deleteLots.execute(entity.id, lots_ids, comment!)
    //TOTEST uncomment below
    // showErrors(lotsUpdateErrorsResponse.errors!)
  }

  const requestedDeletionsCount =
    requestedDeletions.result?.data.data?.deletions?.length ?? lots.length
  const requestedUpdatesCount =
    requestedDeletions.result?.data.data?.updates?.length ?? 0

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
                "Êtes-vous sûr de vouloir supprimer l'integralité de ces lots ?"
              )}
            </strong>{" "}
            {t(
              "Une notification sera envoyé aux sociétés concernées (sans le commentaire)."
            )}
          </p>
          {requestedDeletionsCount > lots.length && (
            <section>
              <Alert
                loading={requestedDeletions.loading}
                icon={AlertCircle}
                variant="warning"
              >
                <span style={{ whiteSpace: "normal" }}>
                  <Trans
                    count={requestedDeletionsCount}
                    defaults="Un total de <b>{{count}} maillons</b> des chaînes de traçabilité dont font partie ces lots seront également supprimés."
                  />
                  {requestedUpdatesCount && (
                    <>
                      {" "}
                      <Trans
                        count={requestedUpdatesCount}
                        defaults="Un total de <b>{{count}} maillons</b> vont être mis à jour."
                      />
                    </>
                  )}
                </span>
              </Alert>
            </section>
          )}
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
        <Button
          variant="warning"
          icon={Edit}
          submit="delete-lots"
          disabled={requestedDeletions.loading}
        >
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
