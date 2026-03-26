import { getBalances } from "accounting/api/biofuels/balances"
import { Balance } from "accounting/types"
import { useFormContext } from "common/components/form2"
import { Notice } from "common/components/notice"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useUnit } from "common/hooks/unit"
import { debounce } from "common/utils/functions"
import { useTranslation } from "react-i18next"
import { Icon } from "common/components/icon"
import { ceilNumber, floorNumber } from "common/utils/formatters"
import { AdvancedFiltersFormProps } from "./advanced-filters.types"
import { hasFiltersSelected } from "./advanced-filters.hooks"

const debouncedGetBalance = debounce(
  (
    entityId,
    biofuel,
    sector,
    category,
    gesBoundMin,
    gesBoundMax,
    feedstock,
    unit
  ) =>
    getBalances({
      page: 1,
      biofuel,
      sector,
      customs_category: category,
      entity_id: entityId,
      ges_bound_min: gesBoundMin,
      ges_bound_max: gesBoundMax,
      feedstock,
      unit,
    }).then((res) =>
      res.data.results.length > 0 ? res.data.results[0] : undefined
    ),
  200
)
export const AvailableBalance = ({ balance }: { balance: Balance }) => {
  const { t } = useTranslation()
  const { formatUnit, unit } = useUnit()
  const entity = useEntity()
  const { value, setField } = useFormContext<AdvancedFiltersFormProps>()

  // Use the available balance from the form if it exists, otherwise use the balance from the props
  const availableBalance = value.availableBalance ?? balance.available_balance
  const _hasFiltersSelected = hasFiltersSelected(value)

  const { loading } = useQuery(debouncedGetBalance, {
    key: "balance-ghg-min-max",
    params: [
      entity.id,
      balance.biofuel?.code,
      balance.sector,
      balance.customs_category,
      value.gesBoundMin ?? balance.ghg_reduction_min,
      value.gesBoundMax ?? balance.ghg_reduction_max,
      value.feedstock,
      unit,
    ],
    executeOnMount: false,
    onSuccess: (data) => {
      if (data) {
        console.log("data", {
          data,
          value,
          balance,
        })
        // When filters are selected, use the ghg reduction min and max from the new data
        // Otherwise, use the default ghg reduction min and max from the balance
        const ghgReductionMin = floorNumber(
          _hasFiltersSelected
            ? data.ghg_reduction_min
            : (value.gesBoundMin ?? balance.ghg_reduction_min),
          1
        )
        const ghgReductionMax = ceilNumber(
          _hasFiltersSelected
            ? data.ghg_reduction_max
            : (value.gesBoundMax ?? balance.ghg_reduction_max),
          1
        )
        setField("availableBalance", data.available_balance)

        if (ghgReductionMin !== value.gesBoundMin) {
          setField("gesBoundMin", ghgReductionMin)
        }

        if (ghgReductionMax !== value.gesBoundMax) {
          setField("gesBoundMax", ghgReductionMax)
        }
      }
    },
  })

  return (
    <Notice noColor variant="info">
      <div>
        {t("Solde disponible pour les filtres sélectionnés")}
        {" : "}
        {loading ? (
          <Icon name="ri-loader-line" size="md" />
        ) : (
          <b>
            {formatUnit(availableBalance, {
              fractionDigits: 0,
            })}
          </b>
        )}
      </div>
    </Notice>
  )
}
