import { getBalances } from "accounting/api/biofuels/balances"
import { Balance } from "accounting/types"
import { useFormContext } from "common/components/form2"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { debounce } from "common/utils/functions"

import { AdvancedFiltersFormProps } from "./advanced-filters.types"
import { useEffect } from "react"
import { mapAdvancedFiltersForPayload } from "./advanced-filters.utils"
import { floorNumber } from "common/utils/formatters"
import { FRACTION_DIGITS_LITERS } from "accounting/config"

const floorAvailableQuantity = (quantity?: number) =>
  floorNumber(quantity ?? 0, FRACTION_DIGITS_LITERS)

const debouncedGetBalance = debounce(
  (entityId, biofuel, sector, category, filters) =>
    getBalances({
      page: 1,
      biofuel,
      sector,
      customs_category: category,
      entity_id: entityId,
      ...mapAdvancedFiltersForPayload(filters),
    }).then((res) => {
      const quantity = floorAvailableQuantity(res.data.total_volume)

      if (quantity <= 1) return undefined

      return res.data.results.length > 0 ? res.data.results[0] : undefined
    }),
  200
)

export const useAvailableBalance = ({ balance }: { balance: Balance }) => {
  const entity = useEntity()
  const { value, setField } = useFormContext<AdvancedFiltersFormProps>()

  const query = useQuery(
    (filters?: AdvancedFiltersFormProps) =>
      debouncedGetBalance(
        entity.id,
        balance.biofuel?.code,
        balance.sector,
        balance.customs_category,
        filters ?? {}
      ),
    {
      key: "balance-ghg-min-max",
      params: [],
      executeOnMount: false,
      executeOnUpdate: false,
      onSuccess: (data) => {
        const availableBalance = floorAvailableQuantity(data?.available_balance)

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
      setField(
        "availableBalance",
        floorAvailableQuantity(balance.available_balance)
      )
  }, [])

  return {
    loading: query.loading,
    getBalance: query.execute,
  }
}
