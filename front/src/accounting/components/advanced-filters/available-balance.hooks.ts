import { getBalances } from "accounting/api/biofuels/balances"
import { Balance } from "accounting/types"
import { useFormContext } from "common/components/form2"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useUnit } from "common/hooks/unit"
import { debounce } from "common/utils/functions"

import { AdvancedFiltersFormProps } from "./advanced-filters.types"
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
    }).then((res) => {
      if (res.data.total_quantity === 0) return undefined

      return res.data.results.length > 0 ? res.data.results[0] : undefined
    }),
  200
)

export const useAvailableBalance = ({
  unit: overrideUnit,
  balance,
}: {
  unit?: ExtendedUnitType
  balance: Balance
}) => {
  const entity = useEntity()
  const { setField } = useFormContext<AdvancedFiltersFormProps>()
  const { unit } = useUnit(overrideUnit)

  const query = useQuery(
    (filters?: AdvancedFiltersFormProps) =>
      debouncedGetBalance(
        entity.id,
        balance.biofuel?.code,
        balance.sector,
        balance.customs_category,
        filters ?? {},
        unit
      ),
    {
      key: "balance-ghg-min-max",
      params: [],
      executeOnMount: false,
      executeOnUpdate: false,
      onSuccess: (data) => {
        const availableBalance = data?.available_balance ?? 0

        setField("availableBalance", availableBalance)
        setField("balance", {
          ...balance,
          available_balance: availableBalance,
        })
      },
    }
  )

  return {
    loading: query.loading,
    getBalance: query.execute,
  }
}
