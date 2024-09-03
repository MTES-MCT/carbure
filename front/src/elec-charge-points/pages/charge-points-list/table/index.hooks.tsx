import { useTranslation } from "react-i18next"
import { ChargePoint } from "../types"
import { ChargePointsListTableStatus } from "./status"

export const useChargePointsColumns = () => {
  const { t } = useTranslation()

  return {
    status: {
      header: t("Statut"),
      cell: (chargePoint: ChargePoint) => (
        <ChargePointsListTableStatus status={chargePoint.status} />
      ),
    },
  }
}
