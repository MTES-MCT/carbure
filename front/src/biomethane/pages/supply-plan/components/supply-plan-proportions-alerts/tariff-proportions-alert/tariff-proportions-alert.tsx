import { Alert } from "common/components/alert2"
import { TariffCoefficientProportions } from "../../../types"
import { useTariffProportionsAlert } from "./tariff-proportions-alert.hooks"

type TariffProportionsAlertProps = {
  loading: boolean
  proportions?: TariffCoefficientProportions
}

export const TariffProportionsAlert = ({
  loading,
  proportions,
}: TariffProportionsAlertProps) => {
  const { shouldDisplay, description } = useTariffProportionsAlert({
    loading,
    proportions,
  })

  if (!shouldDisplay || !description) {
    return null
  }

  return <Alert severity="info" description={description} small />
}
