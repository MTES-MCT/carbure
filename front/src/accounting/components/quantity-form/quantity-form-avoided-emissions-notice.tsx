import { QuantityFormProps } from "./quantity-form.types"
import { Notice } from "common/components/notice"
import { useUnit } from "common/hooks/unit"
import { Trans, useTranslation } from "react-i18next"
import { DEFAULT_UNIT_OPERATION } from "accounting/config"
import { formatTCO2Number } from "accounting/utils/formatters"

type AvoidedEmissionsRecapNoticeProps = Pick<
  QuantityFormProps,
  "quantity" | "avoided_emissions_min" | "avoided_emissions_max"
>

export const AvoidedEmissionsRecapNotice = ({
  quantity,
  avoided_emissions_min,
  avoided_emissions_max,
}: AvoidedEmissionsRecapNoticeProps) => {
  const { t } = useTranslation()
  const { formatUnit } = useUnit(DEFAULT_UNIT_OPERATION)

  if (
    !quantity ||
    !avoided_emissions_min ||
    !avoided_emissions_max ||
    avoided_emissions_min <= 0 ||
    avoided_emissions_max <= 0
  ) {
    return null
  }

  const formattedQuantity = formatUnit(quantity, { fractionDigits: 10 })

  return (
    <Notice noColor variant="info">
      {avoided_emissions_min === avoided_emissions_max ? (
        <Trans
          components={{ strong: <strong /> }}
          t={t}
          values={{
            quantity: formattedQuantity,
            value: formatTCO2Number(avoided_emissions_min),
          }}
          defaults="Pour une quantité de <strong>{{quantity}}</strong>, vous pouvez enregistrer <strong>{{value}} tCO2 évitées</strong>."
        />
      ) : (
        <Trans
          components={{ strong: <strong /> }}
          t={t}
          values={{
            quantity: formattedQuantity,
            min: formatTCO2Number(avoided_emissions_min),
            max: formatTCO2Number(avoided_emissions_max),
          }}
          defaults="Pour une quantité de <strong>{{quantity}}</strong>, vous pouvez enregistrer entre <strong>{{min}} et {{max}} tCO2 évitées</strong>."
        />
      )}
    </Notice>
  )
}
