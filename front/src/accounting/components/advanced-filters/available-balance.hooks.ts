import { getBalances } from "accounting/api/biofuels/balances"
import { Balance } from "accounting/types"
import { useFormContext } from "common/components/form2"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useUnit } from "common/hooks/unit"
import { debounce } from "common/utils/functions"

import { AdvancedFiltersFormProps } from "./advanced-filters.types"
import { ExtendedUnitType } from "common/types"
import { useEffect } from "react"
import { mapAdvancedFiltersForPayload } from "./advanced-filters.utils"
import { floorNumber } from "common/utils/formatters"

const debouncedGetBalance = debounce(
  (entityId, biofuel, sector, category, filters, unit) =>
    getBalances({
      page: 1,
      biofuel,
      sector,
      customs_category: category,
      entity_id: entityId,
      ...mapAdvancedFiltersForPayload(filters),
      unit,
    }).then((res) => {
      const quantity = floorNumber(res.data.total_quantity ?? 0, 0)

      if (quantity === 0) return undefined

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
  const { value, setField } = useFormContext<AdvancedFiltersFormProps>()
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

  // When the component is mounted, set the available balance in the form only if it is not already set
  useEffect(() => {
    if (!value.availableBalance)
      setField("availableBalance", balance.available_balance)
  }, [])

  return {
    loading: query.loading,
    getBalance: query.execute,
  }
}
