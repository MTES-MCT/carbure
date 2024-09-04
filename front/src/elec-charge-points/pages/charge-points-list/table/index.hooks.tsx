import { Cell, Column } from "common/components/table"
import { useTranslation } from "react-i18next"
import { ChargePoint } from "../types"
import { ChargePointsListTableStatus } from "./status"
import { formatDate } from "common/utils/formatters"

export const useChargePointsColumns = () => {
  const { t } = useTranslation()

  const columns: Record<
    | "status"
    | "measure_date"
    | "charge_point_id"
    | "station_id"
    | "current_type"
    | "measure_energy",
    Column<ChargePoint>
  > = {
    status: {
      header: t("Statut"),
      cell: (chargePoint) => (
        <ChargePointsListTableStatus status={chargePoint.status} />
      ),
    },
    measure_date: {
      header: t("Date du dernier relevé"),
      cell: (chargePoint) => (
        <Cell text={formatDate(chargePoint.measure_date)} />
      ),
    },
    charge_point_id: {
      header: t("Identifiant PDC"),
      cell: (chargePoint) => <Cell text={chargePoint.charge_point_id} />,
    },
    station_id: {
      header: t("Identifiant station"),
      cell: (chargePoint) => <Cell text={chargePoint.station_id} />,
    },
    current_type: {
      header: t("CA/CC"),
      cell: (chargePoint) => <Cell text={chargePoint.current_type} />,
    },
    measure_energy: {
      header: t("Dernier index - kWh"),
      cell: (chargePoint) => <Cell text={chargePoint.measure_energy} />,
    },
  }

  return columns
}
