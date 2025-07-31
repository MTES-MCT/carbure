import { Column, Cell } from "common/components/table2"
import { useTranslation } from "react-i18next"
import { ElecDataQualichargeOverview } from "./types"
import { QualichargeBadge } from "elec-charge-points/components/qualicharge/qualicharge-badge"
import { formatDate } from "common/utils/formatters"

export const useQualichargeColumns = () => {
  const { t } = useTranslation()
  const columns: Column<ElecDataQualichargeOverview>[] = [
    {
      header: t("Statut"),
      cell: (data) => <QualichargeBadge status={data.validated_by} />,
    },
    {
      header: t("Unité d'exploitation"),
      cell: (data) => <Cell text={data.operating_unit} />,
    },
    {
      header: t("Station ID"),
      cell: (data) => <Cell text={data.station_id} />,
    },
    {
      header: t("Début de la mesure"),
      cell: (data) => <Cell text={formatDate(data.date_from)} />,
    },
    {
      header: t("Fin de la mesure"),
      cell: (data) => <Cell text={formatDate(data.date_to)} />,
    },
    {
      header: t("Energie (MWh)"),
      cell: (data) => <Cell text={data.energy_amount} />,
    },
  ]

  return columns
}
