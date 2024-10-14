import { Cell, Column } from "common/components/table"
import { useTranslation } from "react-i18next"
import IsArticle2 from "./is-article-2"
import { ChargePoint } from "elec-charge-points/types"
import { ChargePointStatusTag } from "../charge-point-status-tag"
import { formatDate } from "common/utils/formatters"

export const useChargePointsColumns = () => {
  const { t } = useTranslation()

  const columns: Record<
    | "status"
    | "latest_meter_reading_date"
    | "charge_point_id"
    | "station_id"
    | "current_type"
    | "measure_energy"
    | "is_article_2",
    Column<ChargePoint>
  > = {
    status: {
      header: t("Statut"),
      cell: (chargePoint) => (
        <ChargePointStatusTag status={chargePoint.status} />
      ),
    },
    latest_meter_reading_date: {
      header: t("Date du dernier relevé"),
      cell: (chargePoint) => (
        <Cell text={formatDate(chargePoint.latest_meter_reading_date)} />
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
      header: t("Dernier index en kWh"),
      cell: (chargePoint) => <Cell text={chargePoint.measure_energy} />,
    },
    is_article_2: {
      header: t("Relevé trimestriel"),
      cell: (chargePoint) => (
        <IsArticle2 is_article_2={chargePoint.is_article_2} />
      ),
    },
  }

  return columns
}
