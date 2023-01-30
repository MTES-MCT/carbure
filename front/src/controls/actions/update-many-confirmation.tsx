import { AxiosError } from "axios"
import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import Form from "common/components/form"
import { AlertCircle, Edit, Return } from "common/components/icons"
import { TextInput } from "common/components/input"
import { useNotify } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useMutation, useQuery } from "common/hooks/async"
import { LotsUpdateError, LotsUpdateResponse } from "controls/types"
import { LotFormValue } from "lot-add/components/lot-form"
import { useMemo, useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { Lot } from "transactions/types"
import * as api from "../api/admin"
import { UpdateErrorsDialog } from "./update-many-errors"

interface UpdateManyConfirmationDialogProps {
  onClose: () => void
  onSuccess: () => void
  lots: Lot[]
  updatedValues: Partial<LotFormValue>
}
const UpdateManyConfirmationDialog = ({
  onClose,
  onSuccess,
  lots,
  updatedValues,
}: UpdateManyConfirmationDialogProps) => {
  const { t } = useTranslation()
  const [comment, setComment] = useState<string | undefined>()
  const entity = useEntity()
  const notify = useNotify()
  const portal = usePortal()

  const lots_ids = useMemo(() => lots.map((l) => l.id), [lots])

  const requestedUpdates = useQuery(api.updateLots, {
    key: "check-updates",
    params: [entity.id, lots_ids, updatedValues, "check", true],
  })

  const updateLots = useMutation(api.updateLots, {
    invalidates: ["controls"],
    onSuccess: () => {
      notify(
        t("Les {{count}} lots sélectionnés ont bien été modifiés.", {
          count: lots.length,
        }),
        { variant: "success" }
      )
      onSuccess()
    },
    onError: (err) => {
      const errors = (err as AxiosError<LotsUpdateResponse>).response?.data
        .errors
      errors && showErrors(errors!)
    },
  })

  let updatedValuesNames = Object.keys(updatedValues)
    .map((field) => t(field, { ns: "fields" }))
    .join(", ")

  const entities_to_notify: string = getLotsEntitiesToNotify(lots)

  const showErrors = (errors: LotsUpdateError[]) => {
    portal((close) => (
      <UpdateErrorsDialog onClose={close} errors={errors} method="update" />
    ))
  }

  const submit = () => {
    return updateLots.execute(
      entity.id,
      lots_ids,
      updatedValues,
      comment!,
      true
    )

    //TOTEST uncomment below
    // showErrors(lotsUpdateErrorsResponse.errors!)
  }

  const requestedUpdatesCount =
    requestedUpdates.result?.data.data?.updates?.length ?? lots.length

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>
          {t("{{count}} lots vont être modifiés.", {
            count: lots.length,
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
            </strong>{" "}
            {t(
              "Une notification sera envoyée aux sociétés concernées avec votre commentaire."
            )}
          </p>
        </section>

        <section>
          <Alert
            loading={requestedUpdates.loading}
            icon={AlertCircle}
            variant="warning"
          >
            <span style={{ whiteSpace: "normal" }}>
              <Trans
                count={requestedUpdatesCount}
                defaults="Un total de <b>{{count}} maillons</b> des chaînes de traçabilité dont font partie ces lots seront impactés par ces changements."
              />
            </span>
          </Alert>
        </section>

        <section>
          <Form id="edit-lots" onSubmit={submit}>
            <TextInput
              value={comment}
              label={t("Commentaire")}
              onChange={setComment}
              required
              placeholder={t("Entrez un commentaire...")}
            />
          </Form>
          <p>
            {t("Valeurs modifiées")} : <strong>{updatedValuesNames}</strong>
          </p>
          <p>
            {t("Sociétés concernées")} : <strong>{entities_to_notify}</strong>
          </p>
        </section>
      </main>

      <footer>
        <Button
          loading={requestedUpdates.loading || updateLots.loading}
          variant="warning"
          icon={Edit}
          submit="edit-lots"
        >
          {t("Modifier les {{count}} entrées", {
            count: requestedUpdatesCount,
          })}
        </Button>

        <Button icon={Return} action={onClose}>
          {t("Annuler")}
        </Button>
      </footer>
    </Dialog>
  )
}

export default UpdateManyConfirmationDialog

export const getLotsEntitiesToNotify = (lots: Lot[]) => {
  const entities_to_notify: string[] = []
  lots.forEach((lot) => {
    if (lot.carbure_client) {
      entities_to_notify.push(lot.carbure_client.name)
    }
  })
  return entities_to_notify
    .filter((e, i) => entities_to_notify.indexOf(e) == i)
    .join(", ")
}
