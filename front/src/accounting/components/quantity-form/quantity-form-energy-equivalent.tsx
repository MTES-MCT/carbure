import { FRACTION_DIGITS_GJ, FRACTION_DIGITS_LITERS } from "accounting/config"
import { energyFromLiters } from "accounting/pages/teneur/utils/liters"
import { Notice } from "common/components/notice"
import { formatNumber } from "common/utils/formatters"
import { useEffect, useRef } from "react"
import { Trans, useTranslation } from "react-i18next"

type EnergyEquivalentNoticeProps = {
  quantityLiters: number
  pciLitre: number
  renewableEnergyShare: number
}

const scrollEnergyEquivalentIntoView = (
  element: HTMLElement | null | undefined
) => {
  requestAnimationFrame(() => {
    element?.scrollIntoView({ behavior: "smooth", block: "nearest" })
  })
}

export const EnergyEquivalentNotice = ({
  quantityLiters,
  pciLitre,
  renewableEnergyShare,
}: EnergyEquivalentNoticeProps) => {
  const { t } = useTranslation()
  const energyGj = energyFromLiters(
    quantityLiters,
    pciLitre,
    renewableEnergyShare
  ).gj
  const rootRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollEnergyEquivalentIntoView(rootRef.current)
  }, [])

  return (
    <div ref={rootRef}>
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
              liters: formatNumber(quantityLiters, {
                fractionDigits: FRACTION_DIGITS_LITERS,
              }),
              energy: formatNumber(energyGj, {
                fractionDigits: FRACTION_DIGITS_GJ,
              }),
            }}
            defaults="<strong>{{liters}} L</strong> → <strong>{{energy}} GJ</strong>"
          />
        </span>
      </Notice>
    </div>
  )
}
