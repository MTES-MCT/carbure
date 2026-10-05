import { Cell, Column, Order, Table } from "common/components/table2"
import { YesNoIndicator } from "common/components/yes-no-indicator"
import { compact } from "common/utils/collection"
import { formatDate, formatNumber } from "common/utils/formatters"
import { useH2Permissions } from "h2/hooks/use-h2-permissions"
import { H2Station } from "h2/types"
import { formatAccessType } from "h2/utils/formatters"
import { useTranslation } from "react-i18next"
import { useEditStationDialog } from "../edit-station-dialog"

type StationTableProps = {
  loading: boolean
  stations: H2Station[]
  order?: Order
  onOrder: (order: Order | undefined) => void
}

export const StationTable = ({
  loading,
  stations,
  order,
  onOrder,
}: StationTableProps) => {
  const { t } = useTranslation()
  const { canAccessAdmin } = useH2Permissions()

  const showStation = useEditStationDialog()

  const columns: Column<H2Station>[] = compact([
    canAccessAdmin && {
      header: t("Société"),
      cell: (station) => <Cell text={station.entity_name ?? ""} />,
    },
    {
      key: "name",
      header: t("Nom de la station"),
      cell: (station) => <Cell text={station.name} />,
    },
    {
      key: "site_siret",
      header: t("SIRET"),
      cell: (station) => <Cell text={station.site_siret} />,
    },
    {
      header: t("Nature du site"),
      cell: (station) => <Cell text={formatAccessType(station.access_type)} />,
    },
    {
      header: t("Pression (bar)"),
      cell: (station) => (
        <Cell text={station.distributed_pressure.join(" - ")} />
      ),
    },
    {
      key: "distribution_capacity",
      header: t("Distribution (kg / jour)"),
      cell: (station) => (
        <Cell text={formatNumber(station.distribution_capacity)} />
      ),
    },
    {
      header: t("Compatible VP"),
      cell: (station) => (
        <YesNoIndicator value={station.has_personal_vehicle_connector} />
      ),
    },
    {
      key: "commissioning_date",
      header: t("Mis en service le"),
      cell: (station) => (
        <Cell text={formatDate(station.commissioning_date ?? null)} />
      ),
    },
  ])

  return (
    <Table
      loading={loading}
      columns={columns}
      rows={stations}
      order={order}
      onOrder={onOrder}
      onAction={showStation}
    />
  )
}
