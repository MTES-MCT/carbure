import React from "react"

import { Transaction } from "common/types"
import { TransactionSelection } from "transactions/hooks/query/use-selection"
import { Column, Line, TwoLines } from "common/components/table"

import { Box } from "common/components"
import Status from "./status"

import styles from "./list-columns.module.css"
import { EntitySelection } from "carbure/hooks/use-entity"
import { hasDeadline } from "transactions/helpers"
import { Alarm } from "common/components/icons"

export const empty: Column<any> = {
  className: styles.checkboxColumn,
  render: () => null,
}

export const padding: Column<any> = {
  className: styles.paddingColumn,
  render: () => null,
}

export const status: (e: EntitySelection) => Column<Transaction> = (
  entity
) => ({
  header: "Statut",
  className: styles.statusColumn,
  render: (tx) => <Status small transaction={tx} entity={entity} />,
})

export const carbureID: Column<Transaction> = {
  header: "ID",
  render: (tx) => <Line text={tx.lot.carbure_id} />,
}

export const period: (d: string) => Column<Transaction> = (deadline) => ({
  header: "Période",
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

export const periodSimple: Column<Transaction> = {
  header: "Période",
  render: (tx) => <Line text={tx.lot.period} />,
}

export const dae: Column<Transaction> = {
  header: "N° Douane",
  render: (tx) => <Line text={tx.dae} />,
}

export const ghgReduction: Column<Transaction> = {
  header: "Réd. GES",
  sortBy: "ghg_reduction",
  className: styles.narrowColumn,
  render: (tx) => <Line text={`${tx.lot.ghg_reduction}%`} />,
}

export const client: Column<Transaction> = {
  header: "Client",
  sortBy: "client",
  render: (tx) => <Line text={tx.carbure_client?.name ?? tx.unknown_client} />,
}

export const vendor: Column<Transaction> = {
  header: "Fournisseur",
  sortBy: "vendor",
  render: (tx) => <Line text={tx.carbure_vendor?.name ?? tx.unknown_vendor} />,
}

export const addedBy: Column<Transaction> = {
  header: "Ajouté par",
  sortBy: "added_by",
  render: (tx) => <Line text={tx.lot.added_by?.name ?? ""} />,
}

export const biocarburant: Column<Transaction> = {
  header: "Biocarburant (litres)",
  sortBy: "biocarburant",
  render: (tx) => (
    <TwoLines
      text={tx.lot.biocarburant?.name}
      sub={tx.lot.volume.toLocaleString("fr-FR")}
    />
  ),
}

export const volume: Column<Transaction> = {
  header: "Volume",
  sortBy: "volume",
  render: (tx) => <Line text={`${tx.lot.volume}` ?? ""} />,
}

export const matierePremiere: Column<Transaction> = {
  header: "Matiere premiere",
  sortBy: "matiere_premiere",
  render: (tx) => (
    <TwoLines
      text={tx.lot.matiere_premiere?.name}
      sub={tx.lot.pays_origine?.name}
    />
  ),
}

export const productionSite: Column<Transaction> = {
  header: "Site de production",
  sortBy: "pays_origine",
  render: (tx) => (
    <TwoLines
      text={tx.lot.carbure_production_site?.name ?? tx.lot.unknown_production_site} // prettier-ignore
      sub={tx.lot.carbure_production_site?.country.name ?? tx.lot.unknown_production_country?.name ?? ''} // prettier-ignore
    />
  ),
}

export const origine: Column<Transaction> = {
  header: "Usine",
  render: (tx) => (
    <TwoLines
      text={tx.lot.carbure_production_site?.name ?? tx.lot.unknown_production_site_reference} // prettier-ignore
      sub={tx.lot.carbure_production_site?.country.name ?? tx.lot.unknown_production_country?.name ?? ''} // prettier-ignore
    />
  ),
}

export const deliverySite: Column<Transaction> = {
  header: "Site de livraison",
  render: (tx) => {
    const name = tx.carbure_delivery_site?.name ?? tx.unknown_delivery_site
    const country = tx.carbure_delivery_site?.country.name ?? tx.unknown_delivery_site_country?.name ?? '' // prettier-ignore
    const city = tx.carbure_delivery_site?.city
    const location = city ? `${country}, ${city}` : country

    return <TwoLines text={name} sub={location} />
  },
}

export const depot: Column<Transaction> = {
  header: "Dépôt",
  render: (tx) => {
    const name = tx.carbure_delivery_site?.name ?? tx.unknown_delivery_site
    const country = tx.carbure_delivery_site?.country.name ?? tx.unknown_delivery_site_country?.name ?? '' // prettier-ignore
    const city = tx.carbure_delivery_site?.city
    const location = city ? `${country}, ${city}` : country

    return <TwoLines text={name} sub={location} />
  },
}

export const destination: Column<Transaction> = {
  header: "Destination",
  render: (tx) => {
    const name = tx.carbure_delivery_site?.name ?? tx.unknown_delivery_site
    const country = tx.carbure_delivery_site?.country.name ?? tx.unknown_delivery_site_country?.name ?? '' // prettier-ignore
    const city = tx.carbure_delivery_site?.city
    const location = city ? `${country}, ${city}` : country

    return <TwoLines text={name} sub={location} />
  },
}

type Selector = (s: TransactionSelection) => Column<Transaction>

export const selector: Selector = (selection) => ({
  className: styles.checkboxColumn,

  header: (
    <input
      type="checkbox"
      title="Sélectionner toute la page"
      checked={selection.isAllSelected()}
      onChange={(e) => selection.toggleSelectAll(e.target.checked)}
    />
  ),

  render: (tx) => (
    <Box className={styles.checkboxWrapper}>
      <input
        type="checkbox"
        title="Sélectionner le lot"
        checked={selection.has(tx.id)}
        onChange={() => selection.toggleSelect(tx.id)}
        onClick={(e) => e.stopPropagation()}
      />
    </Box>
  ),
})
