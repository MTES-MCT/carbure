import useEntity from "common/hooks/entity"
import Alert from "common/components/alert"
import { Split } from "common/components/icons"
import { useQuery } from "common/hooks/async"
import { formatDate } from "common/utils/formatters"
import { ChargePoint } from "elec-charge-points/types"
import { useTranslation } from "react-i18next"
import * as api from "./api"

type MetersHistoryProps = {
  charge_point_id: ChargePoint["id"]
}

export const MetersHistory = ({ charge_point_id }: MetersHistoryProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const metersHistoryQuery = useQuery(api.getMetersHistory, {
    key: "meters-history",
    params: [entity.id, charge_point_id],
  })

  const metersHistory = metersHistoryQuery?.result?.data.data || []

  if (metersHistoryQuery.loading || metersHistory.length === 0) {
    return null
  }

  return (
    <Alert
      variant="info"
      icon={Split}
      label={t("Historique des numéros de compteur associés")}
    >
      <ul>
        {metersHistory.map((meter) => (
          <li key={meter.id}>
            {formatDate(meter.initial_index_date)} : {meter.mid_certificate}
          </li>
        ))}
      </ul>
    </Alert>
  )
}
