import { TFunction } from "react-i18next"

import { Transaction } from "common/types"
import { TransactionSelection } from "transactions/hooks/query/use-selection"
import { Column, Line, TwoLines } from "common/components/table"

import { Box } from "common/components"
import Status from "./status"

import styles from "./list-columns.module.css"
import { EntitySelection } from "carbure/hooks/use-entity"
import { hasDeadline, prettyVolume } from "transactions/helpers"
import { Alarm } from "common/components/icons"
import { Checkbox } from "common/components/input"

type TxCol = (t: TFunction) => Column<Transaction>

export const empty: Column<any> = {
  className: styles.emptyColumn,
  render: () => null,
}

export const padding: Column<any> = {
  className: styles.paddingColumn,
  render: () => null,
}

export const status: (e: EntitySelection, t: TFunction) => Column<Transaction> =
  (entity, t) => ({
    header: t("Statut"),
    className: styles.statusColumn,
    render: (tx) => <Status small transaction={tx} entity={entity} />,
  })

export const carbureID: TxCol = (t) => ({
  header: t("ID"),
  render: (tx) => <Line text={tx.lot.carbure_id} />,
})

export const period: (
  d: string,
  t: TFunction<"translation">
) => Column<Transaction> = (deadline, t) => ({
  header: t("Période"),
  sortBy: "period",
  className: styles.dateColumn,
  render: (tx) => (
    <>
      <Line
        text={tx.lot.period}
        level={hasDeadline(tx, deadline) ? "warning" : undefined}
      />
      {hasDeadline(tx, deadline) && (
        <Alarm
          color="var(--orange-dark)"
          size={20}
          style={{ marginLeft: 4, marginTop: 2 }}
        />
      )}
    </>
  ),
})

export const periodSimple: TxCol = (t) => ({
  header: t("Période"),
  className: styles.dateColumn,
  sortBy: "period",
  render: (tx) => <Line text={tx.lot.period} />,
})

export const dae: TxCol = (t) => ({
  header: t("N° Douane"),
  sortBy: "delivery_date",
  render: (tx) => <TwoLines text={tx.dae} sub={tx?.delivery_date ?? ""} />,
})

export const ghgReduction: TxCol = (t) => ({
  header: t("Réd. GES"),
  sortBy: "ghg_reduction",
  className: styles.narrowColumn,
  render: (tx) => <Line text={`${tx.lot.ghg_reduction}%`} />,
})

export const client: TxCol = (t) => ({
  header: t("Client"),
  sortBy: "client",
  render: (tx) => <Line text={tx.carbure_client?.name ?? tx.unknown_client} />,
})

export const vendor: TxCol = (t) => ({
  header: t("Fournisseur"),
  sortBy: "vendor",
  render: (tx) => (
    <TwoLines
      text={
        tx.carbure_vendor?.name ??
        (tx.lot.unknown_supplier !== ""
          ? tx.lot.unknown_supplier
          : tx.lot.unknown_supplier_certificate) ??
        "N/A"
      }
      sub={
        tx.lot.carbure_production_site_reference ??
        tx.lot.unknown_production_site_reference
      }
    />
  ),
})

export const addedBy: TxCol = (t) => ({
  header: t("Ajouté par"),
  sortBy: "added_by",
  render: (tx) => <Line text={tx.lot.added_by?.name ?? ""} />,
})

export const biocarburant: TxCol = (t) => ({
  header: t("Biocarburant (litres)"),
  sortBy: "biocarburant",
  render: (tx) => {
    const bc = tx.lot.biocarburant
      ? t(tx.lot.biocarburant.code, { ns: "biofuels" })
      : "N/A"

    return <TwoLines text={bc} sub={prettyVolume(tx.lot.volume)} />
  },
})

export const biocarburantInStock: TxCol = (t) => ({
  header: t("Biocarburant (litres)"),
  sortBy: "biocarburant",
  render: (tx) => {
    const bc = tx.lot.biocarburant
      ? t(tx.lot.biocarburant.code, { ns: "biofuels" })
      : "N/A"

    return (
      <TwoLines
        text={bc}
        sub={`${prettyVolume(tx.lot.remaining_volume)} / ${prettyVolume(
          tx.lot.volume
        )}`}
      />
    )
  },
})

export const volume: TxCol = (t) => ({
  header: t("Volume"),
  sortBy: "volume",
  render: (tx) => <Line text={`${tx.lot.volume}` ?? ""} />,
})

export const matierePremiere: TxCol = (t) => ({
  header: t("Matière première"),
  sortBy: "matiere_premiere",
  render: (tx) => {
    const mp = tx.lot.matiere_premiere
      ? t(tx.lot.matiere_premiere.code, { ns: "feedstocks" })
      : "N/A"

    const ct = tx.lot.pays_origine
      ? t(tx.lot.pays_origine.code_pays, { ns: "countries" })
      : "N/A"

    return <TwoLines text={mp} sub={ct} />
  },
})

export const productionSite: TxCol = (t) => ({
  header: t("Site de production"),
  sortBy: "pays_origine",
  render: (tx) => {
    const country = tx.carbure_delivery_site?.country ?? tx.unknown_delivery_site_country // prettier-ignore
    const countryName = country
      ? t(country?.code_pays, { ns: "countries" })
      : ""

    return (
      <TwoLines
        text={tx.lot.carbure_production_site?.name ?? tx.lot.unknown_production_site} // prettier-ignore
        sub={countryName ?? ''} // prettier-ignore
      />
    )
  },
})

export const origine: TxCol = (t) => ({
  header: t("Usine"),
  sortBy: "pays_origine",
  render: (tx) => {
    const country = tx.carbure_delivery_site?.country ?? tx.unknown_delivery_site_country // prettier-ignore
    const countryName = country
      ? t(country?.code_pays, { ns: "countries" })
      : ""

    return (
      <TwoLines
        text={tx.lot.carbure_production_site?.name ?? tx.lot.unknown_production_site_reference} // prettier-ignore
        sub={countryName ?? ''} // prettier-ignore
      />
    )
  },
})

export const deliverySite: TxCol = (t) => ({
  header: t("Site de livraison"),
  sortBy: "depot",
  render: (tx) => {
    const name = tx.carbure_delivery_site?.name ?? tx.unknown_delivery_site
    const country = tx.carbure_delivery_site?.country ?? tx.unknown_delivery_site_country // prettier-ignore
    const city = tx.carbure_delivery_site?.city

    const countryName = country
      ? t(country?.code_pays, { ns: "countries" })
      : ""

    const location = city ? `${countryName}, ${city}` : countryName

    return <TwoLines text={name} sub={location} />
  },
})

export const depot: TxCol = (t) => ({
  header: t("Dépôt"),
  sortBy: "depot",
  render: (tx) => {
    const name = tx.carbure_delivery_site?.name ?? tx.unknown_delivery_site
    const country = tx.carbure_delivery_site?.country ?? tx.unknown_delivery_site_country // prettier-ignore
    const city = tx.carbure_delivery_site?.city

    const countryName = country
      ? t(country?.code_pays, { ns: "countries" })
      : ""

    const location = city ? `${countryName}, ${city}` : countryName

    return <TwoLines text={name} sub={location} />
  },
})

export const destination: TxCol = (t) => ({
  header: t("Destination"),
  sortBy: "depot",
  render: (tx) => {
    const name = tx.carbure_delivery_site?.name ?? tx.unknown_delivery_site
    const country = tx.carbure_delivery_site?.country ?? tx.unknown_delivery_site_country // prettier-ignore
    const city = tx.carbure_delivery_site?.city

    const countryName = country
      ? t(country?.code_pays, { ns: "countries" })
      : ""

    const location = city ? `${countryName}, ${city}` : countryName

    return <TwoLines text={name} sub={location} />
  },
})

type Selector = (s: TransactionSelection) => Column<Transaction>

export const selector: Selector = (selection) => ({
  className: styles.checkboxColumn,

  header: (
    <Box
      className={styles.checkboxHeaderWrapper}
      onClick={() => selection.toggleSelectAll()}
    >
      <Checkbox
        title="Sélectionner toute la page"
        checked={selection.isAllSelected()}
      />
    </Box>
  ),

  render: (tx) => (
    <Box
      className={styles.checkboxWrapper}
      onClick={(e) => {
        e.stopPropagation()
        selection.toggleSelect(tx.id)
      }}
    >
      <Checkbox title="Sélectionner le lot" checked={selection.has(tx.id)} />
    </Box>
  ),
})
