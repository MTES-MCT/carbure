import { getBalances } from "accounting/api/biofuels/balances"
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
import { ceilNumber, floorNumber } from "common/utils/formatters"

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
  const { value, setField } = useFormContext<TransfertGHGRangeFormProps>()

  const ghgReductionMin = floorNumber(balance?.ghg_reduction_min ?? 50, 1)
  const ghgReductionMax = ceilNumber(balance?.ghg_reduction_max ?? 100, 1)

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
    onSuccess: (data) => {
      if (data) {
        setField("availableBalance", data.available_balance)
      }
    },
  })

  return (
    <>
      {ghgReductionMin !== ghgReductionMax ? (
        <>
          <GHGRangeForm min={ghgReductionMin} max={ghgReductionMax} />
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
        </>
      ) : (
        <Notice noColor variant="info">
          {t("Solde disponible")}
          {" : "}
          <b>
            {formatUnit(
              result?.available_balance ?? balance.available_balance,
              {
                fractionDigits: 0,
              }
            )}
          </b>
          <br />
          {t("Pour un taux de réduction GES de")}
          {" : "}
          <b>{ghgReductionMin}%</b>
        </Notice>
      )}
    </>
  )
}
