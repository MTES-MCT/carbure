import { Alert } from "common/components/alert2"
import { TariffCoefficientProportions } from "../../../types"
import { usePrimaryCropAlert } from "./primary-crop-alert.hooks"

type PrimaryCropAlertProps = {
  loading: boolean
  proportions?: TariffCoefficientProportions
}

export const PrimaryCropAlert = ({
  loading,
  proportions,
}: PrimaryCropAlertProps) => {
  const { description, severity } = usePrimaryCropAlert({
    loading,
    proportions,
  })

  if (!description) {
    return null
  }

  return <Alert severity={severity} description={description} small />
}
