import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import useEntity from "common/hooks/entity"
import { useQuery } from "common/hooks/async"
import { useSelectedEntity } from "common/providers/selected-entity-provider"

import { formatPercentage } from "common/utils/formatters"
import { getTariffCoefficientProportions } from "../../api"
import {
  BiomethaneSupplyInputQuery,
  TariffCoefficientProportions,
} from "../../types"
import { TariffReference } from "biomethane/pages/contract/types"
import {
  isTariffReference2011,
  isTariffReference2020Plus,
} from "./tariff-proportions-alert.utils"
import { useContractProductionUnit } from "biomethane/providers/contract-production-unit"

export type TariffProportionKey = keyof TariffCoefficientProportions

const getVisibleCoefficients = (
  tariffReference?: TariffReference | null
): TariffProportionKey[] => {
  if (isTariffReference2011(tariffReference)) {
    return ["p1", "p2", "p3"]
  }

  if (isTariffReference2020Plus(tariffReference)) {
    return ["p1", "p2", "p3", "p", "peff"]
  }

  return []
}

export const useTariffProportionsAlert = (
  query: BiomethaneSupplyInputQuery
) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { selectedEntityId } = useSelectedEntity()
  const { contractInfos: contract } = useContractProductionUnit()

  const visibleCoefficients = useMemo(
    () => getVisibleCoefficients(contract?.tariff_reference),
    [contract?.tariff_reference]
  )

  const shouldDisplay = visibleCoefficients.length > 0

  const { result: proportions, loading } = useQuery(
    getTariffCoefficientProportions,
    {
      key: "tariff-coefficient-proportions",
      params: [query, entity.id, selectedEntityId],
    }
  )

  const description = useMemo(() => {
    if (loading) {
      return t("Chargement des proportions…")
    }

    if (!proportions) {
      return null
    }

    const proportionsData = proportions.data

    return visibleCoefficients
      .map((key) => `${key} = ${formatPercentage(proportionsData?.[key] ?? 0)}`)
      .join(", ")
  }, [loading, proportions, visibleCoefficients, t])

  return {
    shouldDisplay,
    description,
  }
}
