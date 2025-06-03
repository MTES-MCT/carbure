import { useFormContext } from "common/components/form2"
import { DoubleRange, DoubleRangeProps } from "common/components/inputs2"
import { useTranslation } from "react-i18next"

type GHGRangeFormComponentProps = Omit<DoubleRangeProps, "label">

export type GHGRangeFormProps = {
  gesBoundMin?: number
  gesBoundMax?: number
}
export const GHGRangeForm = (props: GHGRangeFormComponentProps) => {
  const { t } = useTranslation()
  const { bind } = useFormContext<GHGRangeFormProps>()

  return (
    <DoubleRange
      {...props}
      step={0.1}
      suffix="%"
      label={t("Définissez le taux de réduction GES des lots à prélever")}
      minRange={bind("gesBoundMin")}
      maxRange={bind("gesBoundMax")}
    />
  )
}
