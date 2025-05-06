import { getBalances } from "accounting/api/balances"
import { GHGRangeForm } from "accounting/components/ghg-range-form"
import { Balance } from "accounting/types"
import { useFormContext } from "common/components/form2"
import { Notice } from "common/components/notice"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useUnit } from "common/hooks/unit"
import { debounce } from "common/utils/functions"
import { useTranslation } from "react-i18next"
import { TransfertGHGRangeFormProps } from "./ghg-range-form.types"

type TransfertGHGRangeFormComponentProps = {
  balance: Balance
}

const debouncedGetBalance = debounce(
  (
    entityId,
    biofuel,
    sector,
    category,
    ghgReductionMin,
    ghgReductionMax,
    unit
  ) =>
    getBalances({
      page: 1,
      biofuel,
      sector,
      customs_category: category,
      entity_id: entityId,
      ges_bound_min: ghgReductionMin,
      ges_bound_max: ghgReductionMax,
      unit,
    }).then((res) =>
      res.data.results.length > 0 ? res.data.results[0] : undefined
    ),
  200
)

export const TransfertGHGRangeForm = ({
  balance,
}: TransfertGHGRangeFormComponentProps) => {
  const { t } = useTranslation()
  const { formatUnit, unit } = useUnit()
  const entity = useEntity()
  const { value } = useFormContext<TransfertGHGRangeFormProps>()

  const { result } = useQuery(debouncedGetBalance, {
    key: "balance-ghg-min-max",
    params: [
      entity.id,
      balance.biofuel?.code,
      balance.sector,
      balance.customs_category,
      value.gesBoundMin ?? balance.ghg_reduction_min,
      value.gesBoundMax ?? balance.ghg_reduction_max,
      unit,
    ],
    executeOnMount: false,
  })

  return (
    <>
      <GHGRangeForm
        min={Math.floor(balance.ghg_reduction_min)}
        max={Math.ceil(balance.ghg_reduction_max)}
      />
      {
        <Notice noColor variant="info">
          {t("Solde disponible pour ces taux de réduction")}
          {" : "}
          <b>
            {formatUnit(
              result?.available_balance ?? balance.available_balance,
              {
                fractionDigits: 0,
              }
            )}
          </b>
        </Notice>
      }
    </>
  )
}
