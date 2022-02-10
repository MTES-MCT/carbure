import { useMemo, useState } from "react"
import i18next from "i18next"
import { useMatomo } from "matomo"
import { useTranslation } from "react-i18next"
import { Entity, EntityType } from "carbure/types"
import { EntityDepot } from "common/types"
import { Lot, LotQuery } from "transactions/types"
import Menu from "common-v2/components/menu"
import { Check, Return } from "common-v2/components/icons"
import { useMutation, useQuery } from "common-v2/hooks/async"
import * as api from "../api"
import { useNotify } from "common-v2/components/notifications"
import { variations } from "common-v2/utils/formatters"
import Dialog from "common-v2/components/dialog"
import { LotSummary } from "transactions/components/lots/lot-summary"
import Button from "common-v2/components/button"
import { usePortal } from "common-v2/components/portal"
import useEntity from "carbure/hooks/entity"
import { Anchors } from "common-v2/components/dropdown"
import Autocomplete from "common-v2/components/autocomplete"
import * as norm from "common-v2/utils/normalizers"
import { getDeliverySites } from "settings/api"
import { findEntities, findMyCertificates } from "common-v2/api"
import Select from "common-v2/components/select"
import { compact } from "common-v2/utils/collection"

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

  const options = useAcceptOptions({
    query,
    selection,
    summary: true,
  })

  const hasSelection = selection.length > 0

  return (
    <Menu
      disabled={disabled}
      variant="success"
      icon={Check}
      label={hasSelection ? t("Accepter la sélection") : t("Accepter tout")}
      items={options}
    />
  )
}

export interface AcceptOneButtonProps {
  icon?: boolean
  lot: Lot
}

export const AcceptOneButton = ({ icon, lot }: AcceptOneButtonProps) => {
  const { t } = useTranslation()
  const options = useAcceptOptions({ selection: [lot.id] })

  return (
    <Menu
      variant={icon ? "icon" : "success"}
      icon={Check}
      anchor={Anchors.topLeft}
      label={t("Accepter")}
      items={options}
    />
  )
}

function useAcceptOptions(params: {
  query?: LotQuery
  selection?: number[]
  summary?: boolean
}) {
  const portal = usePortal()
  const entity = useEntity()

  // preload processing depots to conditionnaly display the option
  const depots = useQuery(getProcessingDepots, {
    key: "depots",
    params: [entity.id, entity.entity_type],
  })

  const {
    isOperator,
    has_mac,
    has_trading,
    has_stocks,
    has_direct_deliveries,
  } = entity

  const hasProcessing = depots.result !== undefined && depots.result.length > 0

  const query = params.query ?? { entity_id: entity.id }
  const selection = params.selection ?? []
  const summary = params.summary ?? false
  const props = { query, selection, summary }

  return compact([
    isOperator && {
      label: i18next.t("Incorporation"),
      action: () =>
        portal((close) => <BlendingDialog {...props} onClose={close} />),
    },
    isOperator &&
      hasProcessing && {
        label: i18next.t("Incorporation par un tiers"),
        action: () =>
          portal((close) => (
            <ProcessingDialog
              {...props}
              depots={depots.result!}
              onClose={close}
            />
          )),
      },
    has_mac && {
      label: i18next.t("Mise à consommation"),
      action: () =>
        portal((close) => (
          <ReleaseForConsumptionDialog {...props} onClose={close} />
        )),
    },
    has_direct_deliveries && {
      label: i18next.t("Livraison directe"),
      action: () =>
        portal((close) => <DirectDeliveryDialog {...props} onClose={close} />),
    },
    has_stocks && {
      label: i18next.t("Mise en stock"),
      action: () =>
        portal((close) => <InStockDialog {...props} onClose={close} />),
    },
    has_trading && {
      label: i18next.t("Transfert sans stockage"),
      action: () =>
        portal((close) => <TradingDialog {...props} onClose={close} />),
    },
    {
      label: i18next.t("Livraison nationale"),
      action: () =>
        portal((close) => <NationalDialog {...props} onClose={close} />),
    },
    {
      label: i18next.t("Exportation"),
      action: () =>
        portal((close) => <ExportDialog {...props} onClose={close} />),
    },
  ])
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
              "",
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
              "",
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
              "",
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
              "",
              selection.length,
            ])
            acceptLots.execute(query, selection)
          }}
        />
      </footer>
    </Dialog>
  )
}

const NationalDialog = ({
  summary,
  query,
  selection,
  onClose,
}: AcceptDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const matomo = useMatomo()

  const v = variations(selection.length)

  const acceptLots = useMutation(api.acceptForNational, {
    invalidates: ["lots", "snapshot", "lot-details", "lot-summary"],

    onSuccess: () => {
      const text = v({
        zero: t("Les lots ont été marqués comme livraison nationale !"),
        one: t("Le lot a été marqué comme livraison nationale !"),
        many: t("Les lots sélectionnés ont été marqués comme livraison nationale !"), // prettier-ignore
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
            zero: t("Livrer les lots en France"),
            one: t("Livrer le lot en France"),
            many: t("Livrer les lots en France"),
          })}
        </h1>
      </header>
      <main>
        <section>
          {v({
            zero: t("Voulez-vous accepter les lots pour livraison nationale ?"),
            one: t("Voulez-vous accepter le lot pour livraison nationale ?"),
            many: t("Voulez-vous accepter les lots sélectionnés pour livraison nationale ?"), // prettier-ignore
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
              "national",
              "",
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
              "exportation",
              "",
              selection.length,
            ])
            acceptLots.execute(query, selection)
          }}
        />
      </footer>
    </Dialog>
  )
}

// interface AcceptDialogProps {
//   summary?: boolean
//   query: LotQuery
//   selection: number[]
//   onClose: () => void
// }

const TradingDialog = ({
  summary,
  query,
  selection,
  onClose,
}: AcceptDialogProps) => {
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
        zero: t("Les lots ont été transférés !"),
        one: t("Le lot a été transféré !"),
        many: t("Les lots sélectionnés ont été transférés !"),
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
            getOptions={(query) =>
              findMyCertificates(query, { entity_id: entity.id })
            }
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
              "",
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
  depots,
  onClose,
}: AcceptDialogProps & { depots: EntityDepot[] }) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const matomo = useMatomo()

  const v = variations(selection.length)

  const [depot, setDepot] = useState<EntityDepot | undefined>()

  const acceptLots = useMutation(api.acceptForProcessing, {
    invalidates: ["lots", "snapshot", "lot-details", "lot-summary"],

    onSuccess: () => {
      const text = v({
        zero: t("Les lots ont été transférés au tiers !"),
        one: t("Le lot a été transféré au tiers !"),
        many: t("Les lots sélectionnés ont été transférés au tiers !"),
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
              `Les dépôts concernés doivent être enregistrés en tant que "tiers" ou "processing" et l'opérateur tiers doit être indiqué pour apparaître dans la liste ci-dessous.`
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
            options={depots}
            normalize={norm.normalizeEntityDepot}
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
              "",
              selection.length,
            ])
            acceptLots.execute(subquery, selection, depot!.blender!.id)
          }}
        />
      </footer>
    </Dialog>
  )
}

async function getProcessingDepots(entity_id: number, type: EntityType) {
  if (type !== EntityType.Operator) return []

  const depots: EntityDepot[] = await getDeliverySites(entity_id)
  return depots.filter((depot) => depot.blending_is_outsourced)
}
