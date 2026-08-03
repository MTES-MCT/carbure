import { Cell, Column, Table } from "common/components/table2"
import { YesNoIndicator } from "common/components/yes-no-indicator"
import { formatDate, formatNumber } from "common/utils/formatters"
import { H2Station } from "h2/types"
import { useTranslation } from "react-i18next"

type StationTableProps = {
  stations: H2Station[]
}

export const StationTable = ({ stations }: StationTableProps) => {
  const { t } = useTranslation()

  const columns: Column<H2Station>[] = [
    {
      header: t("Nom de la station"),
      cell: (station) => <Cell text={station.name} />,
    },
    {
      header: t("SIRET"),
      cell: (station) => <Cell text={station.site_siret} />,
    },
    {
      header: t("Nature du site"),
      cell: (station) => <Cell text={station.access_type} />,
    },
    {
      header: t("Pression (bar)"),
      cell: (station) => (
        <Cell text={station.distributed_pressure.join(" - ")} />
      ),
    },
    {
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
      header: t("Mis en service le"),
      cell: (station) => (
        <Cell text={formatDate(station.commissioning_date ?? null)} />
      ),
    },
  ]

  return <Table columns={columns} rows={stations} />
}
