import { Alert } from "common/components/alert2"
import { BiomethaneSupplyInputQuery } from "../../types"
import { useTariffProportionsAlert } from "./tariff-proportions-alert.hooks"

type TariffProportionsAlertProps = {
  query: BiomethaneSupplyInputQuery
}

export const TariffProportionsAlert = ({
  query,
}: TariffProportionsAlertProps) => {
  const { shouldDisplay, description } = useTariffProportionsAlert(query)

  if (!shouldDisplay || !description) {
    return null
  }

  return <Alert severity="info" description={description} small />
}
