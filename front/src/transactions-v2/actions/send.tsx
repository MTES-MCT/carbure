import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Lot } from "../types"
import { LotQuery } from "../hooks/lot-query"
import * as api from "../api"
import useEntity from "carbure/hooks/entity"
import { useMutation } from "common-v2/hooks/async"
import { useNotify } from "common-v2/components/notifications"
import { variations } from "common-v2/utils/formatters"
import Button from "common-v2/components/button"
import Checkbox from "common-v2/components/checkbox"
import Dialog from "common-v2/components/dialog"
import { Check, Return } from "common-v2/components/icons"
import { usePortal } from "common-v2/components/portal"
import { Summary } from "../components/lot-summary"

export interface SendButtonProps {
  disabled?: boolean
  query: LotQuery
  selection: number[]
}

export const SendManyButton = ({
  disabled,
  query,
  selection,
}: SendButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      disabled={disabled}
      variant="success"
      icon={Check}
      label={selection.length > 0 ? t("Envoyer sélection") : t("Envoyer tout")}
      action={() =>
        portal((close) => (
          <SendDialog
            summary
            query={query}
            selection={selection}
            onClose={close}
          />
        ))
      }
    />
  )
}

export interface SendIconButtonProps {
  icon?: boolean
  lot: Lot
}

export const SendOneButton = ({ icon, lot }: SendIconButtonProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const portal = usePortal()

  return (
    <Button
      captive
      variant={icon ? "icon" : "success"}
      icon={Check}
      title={t("Envoyer le lot")}
      action={() =>
        portal((close) => (
          <SendDialog
            query={{ entity_id: entity.id }}
            selection={[lot.id]}
            onClose={close}
          />
        ))
      }
    />
  )
}

interface SendDialogProps {
  summary?: boolean
  query: LotQuery
  selection: number[]
  onClose: () => void
}

const SendDialog = ({
  summary,
  query,
  selection,
  onClose,
}: SendDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()

  const [durability, setDurability] = useState(false)
  const [validity, setValidity] = useState(false)

  const v = variations(selection.length)

  const sendLots = useMutation(api.sendLots, {
    invalidates: ["lots", "snapshot"],
    params: [query, selection],

    onSuccess: () => {
      const text = v({
        zero: t("Les lots ont bien été envoyés !"),
        one: t("Le lot a bien été envoyé !"),
        many: t("Les lots sélectionnés ont bien été envoyés !"),
      })

      notify(text, { variant: "success" })
      onClose()
    },

    onError: () => {
      const text = v({
        zero: t("Les lots n'ont pas pu être envoyés !"),
        one: t("Le lot n'a pas pu être envoyé !"),
        many: t("Les lots sélectionnés n'ont pas pu être envoyés !"),
      })

      notify(text, { variant: "danger" })
      onClose()
    },
  })

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>
          {v({
            zero: t("Envoyer tous les brouillons"),
            one: t("Envoyer ce brouillon"),
            many: t("Envoyer les brouillons sélectionnés"),
          })}
        </h1>
      </header>
      <main>
        <section>
          {v({
            zero: t("Vous vous apprêtez à envoyer ces lots à leurs destinataires"), // prettier-ignore
            one: t("Vous vous apprêtez à envoyer ce lot à ses destinataires"),
            many: t("Vous vous apprêtez à envoyer les lots sélectionnés à leurs destinataires"), // prettier-ignore
          })}
          {t(", assurez-vous que les conditions ci-dessous sont respectées :")}
        </section>
        <section>
          <Checkbox
            value={durability}
            onChange={setDurability}
            label={t("Je certifie que cette déclaration respecte les critères de durabilité conformément à la réglementation en vigueur.")} // prettier-ignore
          />
          <Checkbox
            value={validity}
            onChange={setValidity}
            label={t("Je certifie que les informations renseignées sont réelles et valides")} // prettier-ignore
          />
        </section>
        {summary && <Summary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          disabled={sendLots.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
        />
        <Button
          submit
          loading={sendLots.loading}
          disabled={!durability || !validity}
          variant="primary"
          icon={Check}
          label={t("Envoyer")}
          action={sendLots.execute}
        />
      </footer>
    </Dialog>
  )
}
