import { useTranslation } from "react-i18next"
import { Lot, LotQuery } from "transactions-v2/types"
import Menu from "common-v2/components/menu"
import { Check, Return } from "common-v2/components/icons"
import { useMutation } from "common-v2/hooks/async"
import * as api from "../api"
import { useNotify } from "common-v2/components/notifications"
import { variations } from "common-v2/utils/formatters"
import Dialog from "common-v2/components/dialog"
import { LotSummary } from "transactions-v2/components/lots/lot-summary"
import Button from "common-v2/components/button"
import { usePortal } from "common-v2/components/portal"
import useEntity from "carbure/hooks/entity"
import { Anchors } from "common-v2/components/dropdown"

export interface AcceptManyButtonProps {
  disabled?: boolean
  query: LotQuery
  selection: number[]
}

export const AcceptManyButton = ({
  disabled,
  selection,
  query,
}: AcceptManyButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  const props = {
    query,
    selection,
    summary: true,
  }

  return (
    <Menu
      disabled={disabled}
      variant="success"
      icon={Check}
      label={
        selection.length > 0 ? t("Accepter la sélection") : t("Accepter tout")
      }
      items={[
        { label: t("Incorporation") },
        {
          label: t("Mise à consommation"),
          action: () =>
            portal((close) => (
              <ReleaseForConsumptionDialog {...props} onClose={close} />
            )),
        },
        { label: t("Livraison directe") },
      ]}
    />
  )
}

export interface AcceptOneButtonProps {
  icon?: boolean
  lot: Lot
}

export const AcceptOneButton = ({ icon, lot }: AcceptOneButtonProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const portal = usePortal()

  const props = {
    query: { entity_id: entity.id },
    selection: [lot.id],
  }

  return (
    <Menu
      variant={icon ? "icon" : "success"}
      icon={Check}
      anchor={Anchors.topLeft}
      label={t("Accepter le lot")}
      items={[
        { label: t("Incorporation") },
        {
          label: t("Mise à consommation"),
          action: () =>
            portal((close) => (
              <ReleaseForConsumptionDialog {...props} onClose={close} />
            )),
        },
        { label: t("Livraison directe") },
      ]}
    />
  )
}

interface AcceptDialogProps {
  summary?: boolean
  query: LotQuery
  selection: number[]
  onClose: () => void
}

const ReleaseForConsumptionDialog = ({
  summary,
  query,
  selection,
  onClose,
}: AcceptDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()

  const v = variations(selection.length)

  const acceptLots = useMutation(api.acceptReleaseForConsumption, {
    invalidates: ["lots", "snapshot", "lot-details"],

    onSuccess: () => {
      const text = v({
        zero: t("Les lots ont été acceptés pour mise à consommation !"),
        one: t("Le lot a été accepté pour mise à consommation !"),
        many: t("Les lots ont été acceptés pour mise à consommation !"),
      })

      notify(text, { variant: "success" })
      onClose()
    },

    onError: () => {
      const text = v({
        zero: t("Les lots n'ont pas pu être acceptés !"),
        one: t("Le lot n'a pas pu être accepté !"),
        many: t("Les lots sélectionnés n'ont pas pu être acceptés !"),
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
            zero: t("Accepter les lots"),
            one: t("Accepter le lot"),
            many: t("Accepter les lots"),
          })}
        </h1>
      </header>
      <main>
        <section>
          {v({
            zero: t("Voulez-vous accepter ce lot pour mise à consommation ?"),
            one: t("Voulez-vous accepter ce lot pour mise à consommation ?"),
            many: t("Voulez-vous accepter les lots sélectionnés pour mise à consommation ?"), // prettier-ignore
          })}
        </section>
        {summary && <LotSummary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          disabled={acceptLots.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
        />
        <Button
          submit
          loading={acceptLots.loading}
          variant="success"
          icon={Check}
          label={t("Accepter")}
          action={() => acceptLots.execute(query, selection)}
        />
      </footer>
    </Dialog>
  )
}
