import { useMemo, useState } from "react"
import i18next from "i18next"
import { useMatomo } from "matomo"
import { useTranslation } from "react-i18next"
import { EntityType, EntityDepot, type EntityPreview } from "carbure/types"
import { Lot, LotQuery } from "transactions/types"
import Menu from "common/components/menu"
import { Check, Return } from "common/components/icons"
import { useMutation, useQuery } from "common/hooks/async"
import * as api from "../api"
import { useNotify } from "common/components/notifications"
import { variations } from "common/utils/formatters"
import Dialog from "common/components/dialog"
import { LotSummary } from "transactions/components/lots/lot-summary"
import Button from "common/components/button"
import { usePortal } from "common/components/portal"
import useEntity from "carbure/hooks/entity"
import Autocomplete from "common/components/autocomplete"
import * as norm from "carbure/utils/normalizers"
import { getDeliverySites } from "settings/api/delivery-sites"
import { findBiofuelEntities, findMyCertificates } from "carbure/api"
import Select from "common/components/select"
import { compact } from "common/utils/collection"
import Form from "common/components/form"

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
      anchor="top start"
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
    isIndustry,
    isPowerOrHeatProducer,
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
    isIndustry && {
      label: i18next.t("Exportation"),
      action: () =>
        portal((close) => <ExportDialog {...props} onClose={close} />),
    },
    isPowerOrHeatProducer && {
      label: i18next.t("Consommation"),
      action: () =>
        portal((close) => <ConsumptionDialog {...props} onClose={close} />),
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
          {t(
            "En acceptant ces lots, vous indiquez réaliser des mises à consommation de B100 ou ED95."
          )}
        </section>
        {summary && <LotSummary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          autoFocus
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
        <Button
          disabled={acceptLots.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
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
            zero: t("Placer les lots en stock"),
            one: t("Placer le lot en stock"),
            many: t("Placer les lots en stock"),
          })}
        </h1>
      </header>
      <main>
        <section>
          <p>
            {t(
              "Une mise en stock vous permet d'alimenter votre stock sur CarbuRe avec les lots que vous recevez de vos différents fournisseurs. Une fois la procédure terminée, vous pourrez manipuler ces nouveaux stocks depuis l'onglet \"Lots en stock\" de la page Transaction."
            )}
          </p>
        </section>
        {summary && <LotSummary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          autoFocus
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
        <Button
          disabled={acceptLots.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
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
            zero: t("Incorporation des lots"),
            one: t("Incorporation de lot"),
            many: t("Incorporation des lots"),
          })}
        </h1>
      </header>
      <main>
        <section>
          {t(
            "En acceptant ces lots, vous indiquez qu'ils sont utilisés dans le cadre d'incorporations en EFS ou Usine exercée."
          )}
        </section>

        {summary && <LotSummary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          autoFocus
          loading={acceptLots.loading}
          variant="success"
          icon={Check}
          label={t("Incorporation")}
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
        <Button
          disabled={acceptLots.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
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
          {t(
            "En acceptant ces lots pour livraison directe, vous indiquez qu'ils seront utilisés dans le cadre d'incorporations de biocarburant faites à l'étranger mais destinées au marché français"
          )}
        </section>

        {summary && <LotSummary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          autoFocus
          loading={acceptLots.loading}
          variant="success"
          icon={Check}
          label={t("Livraison directe")}
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
        <Button
          disabled={acceptLots.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
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
            zero: t("Exportation des lots"),
            one: t("Exportation de lot"),
            many: t("Exportation des lots"),
          })}
        </h1>
      </header>
      <main>
        <section>
          {t(
            "En acceptant des lots pour exportation, vous indiquez qu'ils sont destinés au marché étranger."
          )}
        </section>

        {summary && <LotSummary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          autoFocus
          loading={acceptLots.loading}
          variant="success"
          icon={Check}
          label={t("Exportation")}
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
        <Button
          disabled={acceptLots.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
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
  const matomo = useMatomo()

  const v = variations(selection.length)

  const [client, setClient] = useState<EntityPreview | string | undefined>()
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
          <p>
            {t(
              "La fonctionnalité de transfert vous permet de transmettre un lot que vous avez reçu de l'un de vos fournisseurs directement vers l'un de vos clients."
            )}
          </p>
          <p>
            {t(
              'Une fois la procédure terminée, vous pourrez retrouver le lot initial de votre fournisseur dans l\'onglet "Lots reçus" ainsi que le lot transféré à votre client dans l\'onglet "Lots envoyés".'
            )}
          </p>
        </section>
        <section>
          <Form
            id="transfer-form"
            onSubmit={() => {
              matomo.push([
                "trackEvent",
                "lots-accept",
                "transfer-without-stock",
                "",
                selection.length,
              ])
              acceptLots.execute(query, selection, client!, certificate!)
            }}
          >
            <Autocomplete
              autoFocus
              required
              label={t("Client")}
              value={client}
              onChange={setClient}
              getOptions={findBiofuelEntities}
              normalize={norm.normalizeEntityPreviewOrUnknown}
              create={norm.identity}
            />
            <Autocomplete
              required
              label={t("Votre certificat de négoce")}
              value={certificate}
              onChange={setCertificate}
              getOptions={(query) =>
                findMyCertificates(query, { entity_id: entity.id })
              }
            />
          </Form>
        </section>
        {summary && <LotSummary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          submit="transfer-form"
          loading={acceptLots.loading}
          disabled={!client || !certificate}
          variant="success"
          icon={Check}
          label={t("Transférer")}
        />
        <Button
          disabled={acceptLots.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
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
            {t(
              "L'incoporation par un tiers (ou processing) consiste à faire réaliser l'incoporation par un opérateur autre que vous-même."
            )}
          </p>
          <p>
            {t(
              `Sur la page "Société", vous pouvez configurer les dépôts concernés par cette pratique lorsque vous précisez comme type de propriété "tiers" ou "processing" et que vous spécifiez l'opérateur tiers qui se chargera des incorporations.`
            )}
          </p>
          <p>
            {t(
              `Une fois le lot accepté, vous pourrez retrouver le lot initial de votre fournisseur dans l'onglet "Lots reçus" ainsi que le lot transféré à l'opérateur tiers dans l'onglet "Lots envoyés".`
            )}
          </p>
        </section>
        <section>
          <Form id="processing">
            <Select
              autoFocus
              label={t("Opérateur tiers")}
              placeholder={t("Choisir une société")}
              value={depot}
              onChange={setDepot}
              options={depots}
              normalize={norm.normalizeEntityDepot}
            />
          </Form>
        </section>
        {depot && summary && (
          <LotSummary query={subquery} selection={selection} />
        )}
      </main>
      <footer>
        <Button
          asideX
          submit="processing"
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
        <Button
          disabled={acceptLots.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
        />
      </footer>
    </Dialog>
  )
}

const ConsumptionDialog = ({
  summary,
  query,
  selection,
  onClose,
}: AcceptDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const matomo = useMatomo()

  const v = variations(selection.length)

  const acceptLots = useMutation(api.acceptForConsumption, {
    invalidates: ["lots", "snapshot", "lot-details", "lot-summary"],

    onSuccess: () => {
      const text = v({
        zero: t("Les lots ont été marqués pour consommation."),
        one: t("Le lot a été marqué pour consommation."),
        many: t("Les lots sélectionnés ont été marqués pour consommation."),
      })

      notify(text, { variant: "success" })
      onClose()
    },

    onError: () => {
      const text = v({
        zero: t("Les lots n'ont pas pu être acceptés."),
        one: t("Le lot n'a pas pu être accepté."),
        many: t("Les lots sélectionnés n'ont pas pu être acceptés."),
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
            zero: t("Consommation des lots"),
            one: t("Consommation de lot"),
            many: t("Consommation des lots"),
          })}
        </h1>
      </header>
      <main>
        <section>
          {t(
            "En acceptant ces lots, vous indiquez qu'ils seront consommés au sein d'une centrale de production d'électricité ou de chaleur."
          )}
        </section>

        {summary && <LotSummary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          autoFocus
          loading={acceptLots.loading}
          variant="success"
          icon={Check}
          label={t("Consommation")}
          action={() => {
            matomo.push([
              "trackEvent",
              "lots-accept",
              "consumption",
              "",
              selection.length,
            ])
            acceptLots.execute(query, selection)
          }}
        />
        <Button
          disabled={acceptLots.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
        />
      </footer>
    </Dialog>
  )
}

async function getProcessingDepots(entity_id: number, type: EntityType) {
  if (type !== EntityType.Operator) return []

  const depots = await getDeliverySites(entity_id)
  return depots.data.data?.filter((depot) => depot.blending_is_outsourced) ?? []
}
