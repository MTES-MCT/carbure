import { AxiosError } from "axios"
import { Entity } from "carbure/types"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import Form from "common/components/form"
import { Edit, Return } from "common/components/icons"
import { TextInput } from "common/components/input"
import { useNotify } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { LotsUpdateError, LotsUpdateErrors as LotsUpdateResponse } from "controls/types"
import { defaultLot, LotFormValue } from "lot-add/components/lot-form"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Lot, LotError } from "transactions/types"
import * as api from "../api/admin"

interface UpdateManyConfirmationDialogProps {
  onClose: () => void
  lots: Lot[]
  updatedValues: Partial<LotFormValue>
}
const UpdateManyConfirmationDialog = ({
  onClose,
  lots,
  updatedValues,
}: UpdateManyConfirmationDialogProps) => {

  const { t } = useTranslation()
  const [comment, setComment] = useState<string | undefined>()
  const notify = useNotify()
  const portal = usePortal()
  const updateLots = useMutation(api.updateLots, {
    invalidates: [
      "controls",
    ],
    onSuccess: () => {
      notify(
        t("Les {{lotCount}} lots sélectionnés ont été modifiés.", {
          lotCount: lots.length,
        }),
        { variant: "success" }
      )
      onClose()
    },
    onError: (err) => {
      const errors = (err as AxiosError<LotsUpdateResponse>).response?.data.errors

      //TODO display errors
    },
  })
    
  let updatedValuesNames = Object.keys(updatedValues).join(', ')
    
  const entities_to_notify: Entity[] = []
  const lots_ids: number[] = []
  lots.forEach((lot) => {
    lots_ids.push(lot.id)
    if (lot.carbure_client) {
      entities_to_notify.push(lot.carbure_client)
    }
  })
  const entities_names = entities_to_notify.map((e) => e.name).join(", ")

  const showErrors = (errors : LotsUpdateError[]) => {
    portal((close) => (
      <UpdateErrorsDialog onClose={close} errors={errors}  />
    ))
  }

  const submit = () => {
    return updateLots.execute(lots_ids, updatedValues, comment!) 

    //TODO test with data below
    // const lotError : LotError= {
    //   error: "NOT_GOOD_VALUE",
    //   is_blocking: true,
    //   field: "biofuel",
    //   fields:null,
    //   value:null,
    //   extra:null,
    //   acked_by_creator: false,
    //   acked_by_recipient: false,
    //   acked_by_admin: false,
    //   acked_by_auditor: false
    // }
    // const lotUpdateError = {lot_id : 329888, errors : [lotError] }
    // const response : LotsUpdateResponse = {
    //   errors : [ lotUpdateError ]
    // }

    // showErrors(response.errors!)

  }

  const editLots = async () => {}

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>
          {t("{{lotCount}} lots vont être modifiés.", {
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
            </strong> {" "}
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
            {t("Valeurs modifiées")} : <strong>{updatedValuesNames}</strong>
          </p>
          <p>
            {t("Sociétés concernées")} : <strong>{entities_names}</strong>
          </p>
        </section>
      </main>

      <footer>
        <Button variant="warning" icon={Edit} action={submit} >
          {t("Modifier les {{lotCount}} lots", {
            lotCount : lots.length}
            )}
        </Button>

        <Button icon={Return} action={onClose}>
          {t("Annuler")}
        </Button>
      </footer>
    </Dialog>
  )
}

export default UpdateManyConfirmationDialog



interface UpdateErrorsDialogProps {
  onClose: () => void
  errors : LotsUpdateError[]
}
const UpdateErrorsDialog = ({
  onClose,
  errors
}: UpdateErrorsDialogProps) => {

    const { t } = useTranslation()
    
    return (
    <Dialog onClose={onClose}>
      <header>
        <h1>
          {t("{{lotErrorCount}} lots vont être modifiés.", {
            lotErrorCount: errors.length
          })}
        </h1>
      </header>
      <main>
        <section>
          <p>
            <strong>
              {t(
                "Les lots ci dessous n’ont pas pu être modifiés : "
              )}
            </strong> 
          </p>
        
          <ul>
            {errors.map(error => {
              return <li key={error.lot_id}>{error.lot_id}</li>
            })}
          </ul>
         
        </section>
      </main>

      <footer>
        <Button  action={onClose}>
          {t("Ok")}
        </Button>
      </footer>
    </Dialog>
  )

}
