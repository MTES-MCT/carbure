import { BiomethaneSupplyInputQuery } from "../../types"
import { PrimaryCropAlert } from "./primary-crop-alert/primary-crop-alert"
import { TariffProportionsAlert } from "./tariff-proportions-alert/tariff-proportions-alert"
import { useSupplyPlanProportions } from "./use-supply-plan-proportions"

type SupplyPlanProportionsAlertsProps = {
  query: BiomethaneSupplyInputQuery
}

export const SupplyPlanProportionsAlerts = ({
  query,
}: SupplyPlanProportionsAlertsProps) => {
  const { loading, proportions } = useSupplyPlanProportions(query)

  return (
    <>
      <TariffProportionsAlert loading={loading} proportions={proportions} />
      <PrimaryCropAlert loading={loading} proportions={proportions} />
    </>
  )
}
