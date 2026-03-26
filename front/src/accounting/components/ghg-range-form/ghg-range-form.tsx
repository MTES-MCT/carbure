import { Balance } from "accounting/types"
import { useFormContext } from "common/components/form2"

import { useTranslation } from "react-i18next"
import { GHGRangeFormProps } from "./ghg-range-form.types"
import { ceilNumber, floorNumber } from "common/utils/formatters"
import { DoubleRange } from "common/components/inputs2"
import { useEffect } from "react"
import { SimpleMenu } from "common/components/menu2"

type GHGRangeFormComponentProps = {
  balance: Balance
  ghgReductionMin?: number
  ghgReductionMax?: number
}

export const GHGRangeForm = ({
  balance,
  ghgReductionMin,
  ghgReductionMax,
}: GHGRangeFormComponentProps) => {
  const { t } = useTranslation()
  const { value, bind, setValue } = useFormContext<GHGRangeFormProps>()

  const _ghgReductionMin = floorNumber(
    ghgReductionMin ?? balance?.ghg_reduction_min ?? 50,
    1
  )
  const _ghgReductionMax = ceilNumber(
    ghgReductionMax ?? balance?.ghg_reduction_max ?? 100,
    1
  )

  // When the component is mounted, init form values with the balance values only if they are not already set
  useEffect(() => {
    const formValue = {
      ...value,
      availableBalance: value.availableBalance ?? balance.available_balance,
      gesBoundMin: value.gesBoundMin ?? floorNumber(balance.ghg_reduction_min),
      gesBoundMax: value.gesBoundMax ?? ceilNumber(balance.ghg_reduction_max),
    }

    setValue(formValue)
  }, [])

  return (
    <DoubleRange
      step={0.1}
      suffix="%"
      label={t("Définissez le taux de réduction GES des lots à prélever")}
      minRange={bind("gesBoundMin")}
      maxRange={bind("gesBoundMax")}
      min={_ghgReductionMin}
      max={_ghgReductionMax}
    />
  )
}

export const GHGRangeFormFilter = ({ balance }: GHGRangeFormComponentProps) => {
  const { t } = useTranslation()
  const { value } = useFormContext<GHGRangeFormProps>()

  const ghgReductionLabel =
    value.gesBoundMin && value.gesBoundMax
      ? `${t("Taux de réduction GES")} : ${value.gesBoundMin}% - ${value.gesBoundMax}%`
      : t("Taux de réduction GES")

  return (
    <SimpleMenu
      buttonProps={{
        children: ghgReductionLabel,
        iconId: "fr-icon-arrow-down-s-line",
        iconPosition: "right",
        priority: "tertiary",
      }}
    >
      {() => (
        <div style={{ padding: "var(--spacing-2w) var(--spacing-3w)" }}>
          <GHGRangeForm balance={balance} />
        </div>
      )}
    </SimpleMenu>
  )
}
