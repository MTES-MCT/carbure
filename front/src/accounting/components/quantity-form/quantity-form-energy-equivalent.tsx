import { FRACTION_DIGITS_GJ } from "accounting/config"
import { computeEnergyGjFromLiters } from "accounting/pages/teneur/utils/formatters"
import { Notice } from "common/components/notice"
import { formatNumber } from "common/utils/formatters"
import { Trans, useTranslation } from "react-i18next"

type EnergyEquivalentNoticeProps = {
  quantityLiters: number
  pciLitre: number
}

export const EnergyEquivalentNotice = ({
  quantityLiters,
  pciLitre,
}: EnergyEquivalentNoticeProps) => {
  const { t } = useTranslation()
  const energyGj = computeEnergyGjFromLiters(quantityLiters, pciLitre)

  return (
    <Notice
      noColor
      variant="info"
      title={t("Équivalent énergétique")}
      style={{ marginTop: "var(--spacing-2v)" }}
    >
      <span aria-live="polite">
        <Trans
          components={{ strong: <strong /> }}
          t={t}
          values={{
            liters: quantityLiters,
            energy: formatNumber(energyGj, {
              fractionDigits: FRACTION_DIGITS_GJ,
            }),
          }}
          defaults="<strong>{{liters}} L</strong> → <strong>{{energy}} GJ</strong>"
        />
      </span>
    </Notice>
  )
}
