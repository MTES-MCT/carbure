import { useTranslation } from "react-i18next"
import { Tag, TagProps, TagVariant } from "common-v2/components/tag"
import { CorrectionStatus, Lot, LotStatus } from "../../types"

export interface LotTagProps extends TagProps {
  lot: Lot
}

export const LotTag = ({ lot, ...props }: LotTagProps) => {
  const { t } = useTranslation()

  let label = t("N/A")
  let variant: TagVariant | undefined = undefined

  if (lot.correction_status === CorrectionStatus.InCorrection) {
    label = t("En correction")
    variant = "warning"
  } else if (lot.correction_status === CorrectionStatus.Fixed) {
    label = t("Corrigé")
    variant = "success"
  } else if (lot.lot_status === LotStatus.Draft) {
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

export default LotTag
