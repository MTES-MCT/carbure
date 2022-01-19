import i18next from "i18next"
import { useTranslation } from "react-i18next"
import { Lot, LotQuery } from "transactions/types"
import Menu from "common-v2/components/menu"
import { Check, Return } from "common-v2/components/icons"
import { useMutation } from "common-v2/hooks/async"
import * as api from "../api"
import { useNotify } from "common-v2/components/notifications"
import { variations } from "common-v2/utils/formatters"
import Dialog from "common-v2/components/dialog"
import { LotSummary } from "transactions/components/lots/lot-summary"
import Button from "common-v2/components/button"
import { usePortal } from "common-v2/components/portal"
import useEntity from "carbure/hooks/entity"
import { Anchors } from "common-v2/components/dropdown"
import { useMatomo } from "matomo"

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
  const hasSelection = selection.length > 0

  return (
    <Menu
      disabled={disabled}
      variant="success"
      icon={Check}
      label={hasSelection ? t("Accepter la sélection") : t("Accepter tout")}
      items={getAcceptOptions(portal, {
        query,
        selection,
        summary: true,
      })}
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

  return (
    <Menu
      variant={icon ? "icon" : "success"}
      icon={Check}
      anchor={Anchors.topLeft}
      label={t("Accepter")}
      items={getAcceptOptions(portal, {
        query: { entity_id: entity.id },
        selection: [lot.id],
      })}
    />
  )
}

function getAcceptOptions(
  portal: ReturnType<typeof usePortal>,
  props: { query: LotQuery; selection: number[]; summary?: boolean }
) {
  return [
    {
      label: i18next.t("Incorporation"),
      action: () =>
        portal((close) => <BlendingDialog {...props} onClose={close} />),
    },
    {
      label: i18next.t("Mise à consommation"),
      action: () =>
        portal((close) => (
          <ReleaseForConsumptionDialog {...props} onClose={close} />
        )),
    },
    {
      label: i18next.t("Livraison directe"),
      action: () =>
        portal((close) => <DirectDeliveryDialog {...props} onClose={close} />),
    },
    {
      label: i18next.t("Exportation"),
      action: () =>
        portal((close) => <ExportDialog {...props} onClose={close} />),
    },
    {
      label: i18next.t("Mise en stock"),
      action: () =>
        portal((close) => <InStockDialog {...props} onClose={close} />),
    },
  ]
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
  const matomo = useMatomo()

  const v = variations(selection.length)

  const acceptLots = useMutation(api.acceptReleaseForConsumption, {
    invalidates: ["lots", "snapshot", "lot-details", "lot-summary"],

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
            zero: t("Mise à consommation des lots"),
            one: t("Mise à consommation du lot"),
            many: t("Mise à consommation des lots"),
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
          label={t("Mise à consommation")}
          action={() => {
            matomo.push([
              "trackEvent",
              "lots-accept",
              "release-for-consumption",
              selection.length,
            ])
            acceptLots.execute(query, selection)
          }}
        />
      </footer>
    </Dialog>
  )
}

const InStockDialog = ({
  summary,
  query,
  selection,
  onClose,
}: AcceptDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const matomo = useMatomo()

  const v = variations(selection.length)

  const acceptLots = useMutation(api.acceptInStock, {
    invalidates: ["lots", "snapshot", "lot-details", "lot-summary"],

    onSuccess: () => {
      const text = v({
        zero: t("Les lots ont été placés dans votre stock !"),
        one: t("Le lot a été placé dans votre stock !"),
        many: t("Les lots sélectionnés ont été placés dans votre stock !"),
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
            zero: t("Voulez-vous accepter ces lots dans votre stock ?"),
            one: t("Voulez-vous accepter ce lot dans votre stock ?"),
            many: t("Voulez-vous accepter les lots sélectionnés dans votre stock ?"), // prettier-ignore
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
          label={t("Mise en stock")}
          action={() => {
            matomo.push([
              "trackEvent",
              "lots-accept",
              "to-stock",
              selection.length,
            ])
            acceptLots.execute(query, selection)
          }}
        />
      </footer>
    </Dialog>
  )
}

const BlendingDialog = ({
  summary,
  query,
  selection,
  onClose,
}: AcceptDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const matomo = useMatomo()

  const v = variations(selection.length)

  const acceptLots = useMutation(api.acceptForBlending, {
    invalidates: ["lots", "snapshot", "lot-details", "lot-summary"],

    onSuccess: () => {
      const text = v({
        zero: t("Les lots ont été marqués pour incorporation !"),
        one: t("Le lot a été marqué pour incorporation !"),
        many: t("Les lots sélectionnés ont été marqués pour incorporation !"),
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
            zero: t("Incorporer les lots"),
            one: t("Incorporer le lot"),
            many: t("Incorporer les lots"),
          })}
        </h1>
      </header>
      <main>
        <section>
          {v({
            zero: t("Voulez-vous accepter les lots pour incorporation ?"),
            one: t("Voulez-vous accepter le lot pour incorporation ?"),
            many: t("Voulez-vous accepter les lots sélectionnés pour incorporation ?"), // prettier-ignore
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
          label={t("Incorporer")}
          action={() => {
            matomo.push([
              "trackEvent",
              "lots-accept",
              "blending",
              selection.length,
            ])
            acceptLots.execute(query, selection)
          }}
        />
      </footer>
    </Dialog>
  )
}

const DirectDeliveryDialog = ({
  summary,
  query,
  selection,
  onClose,
}: AcceptDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const matomo = useMatomo()

  const v = variations(selection.length)

  const acceptLots = useMutation(api.acceptForDirectDelivery, {
    invalidates: ["lots", "snapshot", "lot-details", "lot-summary"],

    onSuccess: () => {
      const text = v({
        zero: t("Les lots ont été marqués comme livraison directe !"),
        one: t("Le lot a été marqué comme livraison directe !"),
        many: t("Les lots sélectionnés ont été marqués comme livraison directe !"), // prettier-ignore
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
            zero: t("Livraison directe des lots"),
            one: t("Livraison directe du lot"),
            many: t("Livraison directe des lots"),
          })}
        </h1>
      </header>
      <main>
        <section>
          {v({
            zero: t("Voulez-vous accepter les lots pour livraison directe ?"),
            one: t("Voulez-vous accepter le lot pour livraison directe ?"),
            many: t("Voulez-vous accepter les lots sélectionnés pour livraison directe ?"), // prettier-ignore
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
          label={t("Livrer")}
          action={() => {
            matomo.push([
              "trackEvent",
              "lots-accept",
              "direct-delivery",
              selection.length,
            ])
            acceptLots.execute(query, selection)
          }}
        />
      </footer>
    </Dialog>
  )
}

const ExportDialog = ({
  summary,
  query,
  selection,
  onClose,
}: AcceptDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const matomo = useMatomo()

  const v = variations(selection.length)

  const acceptLots = useMutation(api.acceptForExport, {
    invalidates: ["lots", "snapshot", "lot-details", "lot-summary"],

    onSuccess: () => {
      const text = v({
        zero: t("Les lots ont été marqués comme exportation !"),
        one: t("Le lot a été marqué comme exportation !"),
        many: t("Les lots sélectionnés ont été marqués comme exportation !"), // prettier-ignore
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
            zero: t("Exporter les lots"),
            one: t("Exporter le lot"),
            many: t("Exporter les lots"),
          })}
        </h1>
      </header>
      <main>
        <section>
          {v({
            zero: t("Voulez-vous accepter les lots pour exportation ?"),
            one: t("Voulez-vous accepter le lot pour exportation ?"),
            many: t("Voulez-vous accepter les lots sélectionnés pour exportation ?"), // prettier-ignore
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
          label={t("Exporter")}
          action={() => {
            matomo.push([
              "trackEvent",
              "lots-accept",
              "direct-delivery",
              selection.length,
            ])
            acceptLots.execute(query, selection)
          }}
        />
      </footer>
    </Dialog>
  )
}
