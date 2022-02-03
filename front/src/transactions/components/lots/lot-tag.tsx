import { useTranslation } from "react-i18next"
import { Tag, TagProps, TagVariant } from "common-v2/components/tag"
import { Lot, LotStatus, CorrectionStatus, DeliveryType } from "../../types"
import useEntity from "carbure/hooks/entity"

export interface LotTagProps extends TagProps {
  lot: Lot
}

export const LotTag = ({ lot, ...props }: LotTagProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  let label = t("N/A")
  let variant: TagVariant | undefined = undefined

  const status = lot.lot_status
  const correction = lot.correction_status
  const delivery = lot.delivery_type

  const isClient = lot.carbure_client?.id === entity.id
  const knowsDelivery = isClient || entity.isAdmin || delivery !== DeliveryType.Unknown

  if (status === LotStatus.Draft) {
    label = t("Brouillon")
  } else if (status === LotStatus.Rejected) {
    label = t("Refusé")
    variant = "danger"
  } else if (correction === CorrectionStatus.InCorrection) {
    label = t("En correction")
    variant = "warning"
  } else if (correction === CorrectionStatus.Fixed) {
    label = t("Corrigé")
    variant = "success"
  } else if (status === LotStatus.Pending) {
    label = t("En attente")
    variant = "info"
  } else if (status === LotStatus.Deleted) {
    label = t("Supprimé")
    variant = "danger"
  } else if (knowsDelivery) {
    variant = "success"
    if (delivery === DeliveryType.Blending) {
      label = t("Incorporé")
    } else if (delivery === DeliveryType.Direct) {
      label = t("Livraison directe")
    } else if (delivery === DeliveryType.Export) {
      label = t("Exporté")
    } else if (delivery === DeliveryType.Processing) {
      label = t("Processing")
    } else if (delivery === DeliveryType.RFC) {
      label = t("Mise à conso.")
    } else if (delivery === DeliveryType.Stock) {
      label = t("Stocké")
    } else if (delivery === DeliveryType.Trading) {
      label = t("Transféré")
    }
  } else if (status === LotStatus.Accepted) {
    variant = "success"
    label = t("Accepté")
  } else if (status === LotStatus.Frozen) {
    variant = "success"
    label = t("Déclaré")
  }

  return <Tag {...props} variant={variant} label={label} />
}

export default LotTag
