import { useMemo } from "react"

import { formatPercentage } from "common/utils/formatters"
import { TariffReference } from "biomethane/pages/contract/types"
import { useContractProductionUnit } from "biomethane/providers/contract-production-unit"
import {
  TariffCoefficientProportions,
  TariffCoefficients,
} from "../../../types"
import {
  isTariffReference2011,
  isTariffReference2020Plus,
} from "./tariff-proportions-alert.utils"

export type TariffProportionKey = keyof TariffCoefficients

const getVisibleCoefficients = (
  tariffReference?: TariffReference | null
): TariffProportionKey[] => {
  if (isTariffReference2011(tariffReference)) {
    return ["p1", "p2", "p3"]
  }

  if (isTariffReference2020Plus(tariffReference)) {
    return ["p1", "p2", "p3", "p", "pef"]
  }

  return []
}

type UseTariffProportionsAlertParams = {
  loading: boolean
  proportions?: TariffCoefficientProportions
}

export const useTariffProportionsAlert = ({
  loading,
  proportions,
}: UseTariffProportionsAlertParams) => {
  const { contractInfos: contract } = useContractProductionUnit()

  const visibleCoefficients = useMemo(
    () => getVisibleCoefficients(contract?.tariff_reference),
    [contract?.tariff_reference]
  )

  const tariffCoefficients = proportions?.tariff_coefficients
  // Null means the feedstock tariff coefficient referential is not ready yet.
  const shouldDisplay =
    visibleCoefficients.length > 0 && !loading && tariffCoefficients != null

  const description = useMemo(() => {
    if (!tariffCoefficients) {
      return null
    }

    return visibleCoefficients
      .map(
        (key) => `${key} = ${formatPercentage(tariffCoefficients[key] ?? 0)}`
      )
      .join(", ")
  }, [tariffCoefficients, visibleCoefficients])

  return {
    shouldDisplay,
    description,
  }
}
