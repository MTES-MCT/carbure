import { useMemo, useState } from "react"
import i18next from "i18next"
import { useTranslation } from "react-i18next"
import { Lot, LotQuery } from "transactions-v2/types"
import Menu from "common-v2/components/menu"
import { Check, Return } from "common-v2/components/icons"
import { useQuery, useMutation } from "common-v2/hooks/async"
import * as api from "../api"
import { useNotify } from "common-v2/components/notifications"
import { variations } from "common-v2/utils/formatters"
import Dialog from "common-v2/components/dialog"
import { LotSummary } from "transactions-v2/components/lots/lot-summary"
import Button from "common-v2/components/button"
import { usePortal } from "common-v2/components/portal"
import useEntity from "carbure/hooks/entity"
import { Anchors } from "common-v2/components/dropdown"
import { Entity } from "carbure/types"
import Autocomplete from "common-v2/components/autocomplete"
import { findEntities } from "common-v2/api"
import { getDeliverySites } from "settings/api"
import * as norm from "common-v2/utils/normalizers"
import Select from "common-v2/components/select"
import { Normalizer } from "common-v2/utils/normalize"
import { EntityDeliverySite } from "settings/hooks/use-delivery-sites"
import { findCertificates } from "common/api"

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
      label={t("Accepter le lot")}
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
      label: i18next.t("Incorporation par un tiers"),
      action: () =>
        portal((close) => <ProcessingDialog {...props} onClose={close} />),
    },
    {
      label: i18next.t("Mise à consommation"),
      action: () =>
        portal((close) => (
          <ReleaseForConsumptionDialog {...props} onClose={close} />
        )),
    },
    {
      label: i18next.t("Mise en stock"),
      action: () =>
        portal((close) => <InStockDialog {...props} onClose={close} />),
    },
    {
      label: i18next.t("Transfert sans stockage"),
      action: () =>
        portal((close) => <TradingDialog {...props} onClose={close} />),
    },
    {
      label: i18next.t("Livraison directe"),
      action: () =>
        portal((close) => <ExportDialog {...props} onClose={close} />),
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
          label={t("Mise à consommation")}
          action={() => acceptLots.execute(query, selection)}
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
          action={() => acceptLots.execute(query, selection)}
        />
      </footer>
    </Dialog>
  )
}

const TradingDialog = ({
  summary,
  query,
  selection,
  onClose,
}: AcceptDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const entity = useEntity()

  const v = variations(selection.length)

  const [client, setClient] = useState<Entity | string | undefined>()
  const [certificate, setCertificate] = useState<string | undefined>()

  const acceptLots = useMutation(api.acceptForTrading, {
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
            zero: t("Transférer les lots"),
            one: t("Transférer le lot"),
            many: t("Transférer les lots"),
          })}
        </h1>
      </header>
      <main>
        <section>
          {v({
            zero: t("Voulez-vous transférer ces lots ?"),
            one: t("Voulez-vous transférer ce lot ?"),
            many: t("Voulez-vous transférer les lots sélectionnés ?"),
          })}
        </section>
        <section>
          <Autocomplete
            label={t("Destinataire")}
            value={client}
            onChange={setClient}
            getOptions={findEntities}
            normalize={norm.normalizeEntity}
            create={norm.identity}
          />
          <Autocomplete
            label={t("Certificat")}
            value={certificate}
            onChange={setCertificate}
            getOptions={(query) => findCertificates(query, entity.id)}
          />
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
          disabled={!client || !certificate}
          variant="success"
          icon={Check}
          label={t("Transférer")}
          action={() =>
            acceptLots.execute(query, selection, client!, certificate!)
          }
        />
      </footer>
    </Dialog>
  )
}

const ProcessingDialog = ({
  summary,
  query,
  selection,
  onClose,
}: AcceptDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const entity = useEntity()

  const v = variations(selection.length)

  const [depot, setDepot] = useState<EntityDeliverySite | undefined>()

  const depots = useQuery(getDeliverySites, {
    key: "depots",
    params: [entity.id],
  })

  const acceptLots = useMutation(api.acceptForProcessing, {
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

  const subquery = useMemo(
    () => ({
      ...query,
      delivery_sites: depot ? [depot.depot!.depot_id] : [],
    }),
    [query, depot]
  )

  const processingDepots = (depots.result ?? []).filter(
    (depot) => depot.blending_is_outsourced
  )

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>
          {v({
            zero: t("Transférer les lots"),
            one: t("Transférer le lot"),
            many: t("Transférer les lots"),
          })}
        </h1>
      </header>
      <main>
        <section>
          {t(
            "Vous pouvez transférer vos lots reçus dans un dépôt pour lequel l'incorporation peut être effectuée par une société tierce."
          )}
        </section>
        <section>
          <Select
            label={t("Société tierce")}
            placeholder={t("Choisir une société")}
            value={depot}
            onChange={setDepot}
            options={processingDepots}
            normalize={normalizeEntityDepot}
          />
        </section>
        {summary && <LotSummary query={subquery} selection={selection} />}
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
          disabled={!depot}
          variant="success"
          icon={Check}
          label={t("Transférer")}
          action={() =>
            acceptLots.execute(subquery, selection, depot!.blender!.id)
          }
        />
      </footer>
    </Dialog>
  )
}

// prettier-ignore
const normalizeEntityDepot: Normalizer<EntityDeliverySite> = (depot) => ({
  label: `${depot.blender!.name} - ${depot.depot!.name}`,
  value: depot
})

const BlendingDialog = ({
  summary,
  query,
  selection,
  onClose,
}: AcceptDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()

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
            zero: t("Accepter les lots"),
            one: t("Accepter le lot"),
            many: t("Accepter les lots"),
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
          action={() => acceptLots.execute(query, selection)}
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

  const v = variations(selection.length)

  const acceptLots = useMutation(api.acceptForExport, {
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
            zero: t("Accepter les lots"),
            one: t("Accepter le lot"),
            many: t("Accepter les lots"),
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
          action={() => acceptLots.execute(query, selection)}
        />
      </footer>
    </Dialog>
  )
}
