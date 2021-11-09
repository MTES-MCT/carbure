import { useTranslation } from "react-i18next"
import { Tag, TagProps, TagVariant } from "common-v2/components/tag"

import { Lot, LotStatus } from "../types"

export interface StatusProps extends TagProps {
  lot: Lot
}

const Status = ({ lot, ...props }: StatusProps) => {
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

export default Status
