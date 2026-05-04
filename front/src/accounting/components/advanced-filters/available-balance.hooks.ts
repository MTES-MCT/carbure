import { getBalances } from "accounting/api/biofuels/balances"
import { useFormContext } from "common/components/form2"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useUnit } from "common/hooks/unit"
import { debounce } from "common/utils/functions"

import {
  AdvancedFiltersFormProps,
  AdvancedFiltersWithBalanceFormProps,
} from "./advanced-filters.types"
import { ExtendedUnitType } from "common/types"

const pickFilters = (filters: AdvancedFiltersFormProps) => {
  return {
    ges_bound_min: filters.gesBoundMin,
    ges_bound_max: filters.gesBoundMax,
    feedstock: filters.feedstock,
    durability_period: filters.durability_period,
    origin_country: filters.origin_country,
  }
}
const debouncedGetBalance = debounce(
  (entityId, biofuel, sector, category, filters, unit) =>
    getBalances({
      page: 1,
      biofuel,
      sector,
      customs_category: category,
      entity_id: entityId,
      ...pickFilters(filters),
      unit,
    }).then((res) =>
      res.data.results.length > 0 ? res.data.results[0] : undefined
    ),
  200
)

export const useAvailableBalance = ({
  unit: overrideUnit,
}: {
  unit?: ExtendedUnitType
}) => {
  const entity = useEntity()
  const { value, setField } =
    useFormContext<AdvancedFiltersWithBalanceFormProps>()
  const { unit } = useUnit(overrideUnit)

  const query = useQuery(
    (filters?: AdvancedFiltersFormProps) =>
      debouncedGetBalance(
        entity.id,
        value.balance.biofuel?.code,
        value.balance.sector,
        value.balance.customs_category,
        filters ?? {},
        unit
      ),
    {
      key: "balance-ghg-min-max",
      params: [],
      executeOnMount: false,
      executeOnUpdate: false,
      onSuccess: (data) => {
        if (data) {
          setField("availableBalance", data.available_balance)
        }
      },
    }
  )

  return {
    loading: query.loading,
    getBalance: query.execute,
  }
}
