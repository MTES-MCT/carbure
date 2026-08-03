import useEntity from "common/hooks/entity"
import { useQuery } from "common/hooks/async"
import { useSelectedEntity } from "common/providers/selected-entity-provider"

import { getTariffCoefficientProportions } from "../../api"
import { BiomethaneSupplyInputQuery } from "../../types"

export const useSupplyPlanProportions = (query: BiomethaneSupplyInputQuery) => {
  const entity = useEntity()
  const { selectedEntityId } = useSelectedEntity()

  const { result, loading } = useQuery(getTariffCoefficientProportions, {
    key: "tariff-coefficient-proportions",
    params: [query, entity.id, selectedEntityId],
  })

  return {
    loading,
    proportions: result?.data,
  }
}
