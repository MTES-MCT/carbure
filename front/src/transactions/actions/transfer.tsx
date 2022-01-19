import { useMemo, useState } from "react"
import i18next from "i18next"
import { useTranslation } from "react-i18next"
import { Lot, LotQuery } from "transactions/types"
import Menu from "common-v2/components/menu"
import { Check, Return } from "common-v2/components/icons"
import { useQuery, useMutation } from "common-v2/hooks/async"
import * as api from "../api"
import { useNotify } from "common-v2/components/notifications"
import { variations } from "common-v2/utils/formatters"
import Dialog from "common-v2/components/dialog"
import { LotSummary } from "transactions/components/lots/lot-summary"
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
import { useMatomo } from "matomo"

export interface TransferManyButtonProps {
  disabled?: boolean
  query: LotQuery
  selection: number[]
}

export const TransferManyButton = ({
  disabled,
  selection,
  query,
}: TransferManyButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Menu
      disabled={disabled || selection.length === 0}
      variant="primary"
      icon={Check}
      label={t("Transférer la sélection")}
      items={getTransferOptions(portal, {
        query,
        selection,
        summary: true,
      })}
    />
  )
}

export interface TransferOneButtonProps {
  icon?: boolean
  lot: Lot
}

export const TransferOneButton = ({ icon, lot }: TransferOneButtonProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const portal = usePortal()

  return (
    <Menu
      variant={icon ? "icon" : "primary"}
      icon={Check}
      anchor={Anchors.topLeft}
      label={t("Transférer")}
      items={getTransferOptions(portal, {
        query: { entity_id: entity.id },
        selection: [lot.id],
      })}
    />
  )
}

function getTransferOptions(
  portal: ReturnType<typeof usePortal>,
  props: { query: LotQuery; selection: number[]; summary?: boolean }
) {
  return [
    {
      label: i18next.t("Incorporation par un tiers"),
      action: () =>
        portal((close) => <ProcessingDialog {...props} onClose={close} />),
    },

    {
      label: i18next.t("Transfert sans stockage"),
      action: () =>
        portal((close) => <TradingDialog {...props} onClose={close} />),
    },
  ]
}

interface TransferDialogProps {
  summary?: boolean
  query: LotQuery
  selection: number[]
  onClose: () => void
}

const TradingDialog = ({
  summary,
  query,
  selection,
  onClose,
}: TransferDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const entity = useEntity()
  const matomo = useMatomo()

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
            normalize={norm.normalizeEntityOrUnknown}
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
          action={() => {
            matomo.push([
              "trackEvent",
              "lots-accept",
              "transfer-without-stock",
              selection.length,
            ])
            acceptLots.execute(query, selection, client!, certificate!)
          }}
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
}: TransferDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const entity = useEntity()
  const matomo = useMatomo()

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
      delivery_sites: depot ? [depot.depot!.name] : query.delivery_sites,
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
            zero: t("Incorporation des lots par un tiers"),
            one: t("Incorporation du lot par un tiers"),
            many: t("Incorporation des lots par un tiers"),
          })}
        </h1>
      </header>
      <main>
        <section>
          <p>
            {t("Les lots incorporés par un tiers doivent lui être transférés.")}
          </p>
          <p>
            {t(
              `Les dépôts concernés doivent être enregistrés en tant que "tiers" ou "processing" \net l'opérateur tiers doit être indiqué pour apparaître dans la liste ci-dessous.`
            )}
          </p>
          {/* Plus d'informations sur le processing sur [Guide] */}
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
        {depot && summary && (
          <LotSummary query={subquery} selection={selection} />
        )}
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
          label={t("Transférer à un tiers")}
          action={() => {
            matomo.push([
              "trackEvent",
              "lots-accept",
              "processing",
              selection.length,
            ])
            acceptLots.execute(subquery, selection, depot!.blender!.id)
          }}
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
