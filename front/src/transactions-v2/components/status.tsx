import { useTranslation } from "react-i18next"
import { Tag, TagProps, TagVariant } from "common-v2/components/tag"

import { Lot, Stock, LotStatus } from "../types"

export interface LotTagProps extends TagProps {
  lot: Lot
}

export const LotTag = ({ lot, ...props }: LotTagProps) => {
  const { t } = useTranslation()

  let label = t("N/A")
  let variant: TagVariant | undefined = undefined

  if (lot.lot_status === LotStatus.Draft) {
    label = t("Brouillon")
  } else if (lot.lot_status === LotStatus.Pending) {
    label = t("En attente")
    variant = "info"
  } else if (lot.lot_status === LotStatus.Accepted) {
    label = t("Accepté")
    variant = "success"
  } else if (lot.lot_status === LotStatus.Rejected) {
    label = t("Refusé")
    variant = "danger"
  } else if (lot.lot_status === LotStatus.Frozen) {
    label = t("Déclaré")
    variant = "success"
  }

  return <Tag {...props} variant={variant} label={label} />
}

export interface StockTagProps extends TagProps {
  stock: Stock
}

export const StockTag = ({ stock, ...props }: StockTagProps) => {
  const { t } = useTranslation()

  let label = t("N/A")
  let variant: TagVariant | undefined = undefined

  if (stock.remaining_volume === stock.initial_volume) {
    variant = 'success'
    label = t("En stock")
  } else if (stock.remaining_volume > 0) {
    variant = 'info'
    label = t("Entamé")
  } else {
    label = t("Vide")
  }

  return <Tag {...props} variant={variant} label={label} />
}