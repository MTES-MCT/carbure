import { useTranslation } from "react-i18next"
import { Tag, TagProps, TagVariant } from "common/components/tag"
import { Lot, LotStatus, CorrectionStatus, DeliveryType } from "../../types"
import useEntity from "carbure/hooks/entity"
import {
	AlertTriangle,
	Certificate,
	CheckCircle,
} from "common/components/icons"

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
	const knowsDelivery = (isClient || entity.isAdmin) && delivery !== DeliveryType.Unknown // prettier-ignore

	if (status === LotStatus.Draft) {
		label = t("Brouillon")
	} else if (status === LotStatus.Rejected) {
		label = t("Refusé")
		variant = "danger"
	} else if (status === LotStatus.Deleted) {
		label = t("Supprimé")
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
	} else if (knowsDelivery) {
		variant = "success"
		if (delivery === DeliveryType.Blending) {
			label = t("Incorporé")
		} else if (delivery === DeliveryType.Direct) {
			label = t("Livr. directe")
		} else if (delivery === DeliveryType.Exportation) {
			label = t("Exporté")
		} else if (delivery === DeliveryType.Processing) {
			label = t("Processing")
		} else if (delivery === DeliveryType.RFC) {
			label = t("Mise à conso.")
		} else if (delivery === DeliveryType.Stock) {
			label = t("Stocké")
		} else if (delivery === DeliveryType.Trading) {
			label = t("Transféré")
		} else if (delivery === DeliveryType.Flushed) {
			label = t("Vidé")
		} else {
			label = t("Accepté")
		}
	} else if (status === LotStatus.Accepted) {
		variant = "success"
		label = t("Accepté")
	} else if (status === LotStatus.Frozen) {
		variant = "success"
		label = t("Déclaré")
	}

	return (
		<Tag {...props} variant={variant}>
			{lot.lot_status === LotStatus.Frozen && (
				<Certificate title={t("Lot déclaré")} />
			)}

			{label}

			{lot.audit_status === "NONCONFORM" && (
				<AlertTriangle color="var(--red-dark)" title={t("Non conforme")} />
			)}
			{lot.audit_status === "CONFORM" && (
				<CheckCircle color="var(--green-dark)" title={t("Conforme")} />
			)}
		</Tag>
	)
}

export default LotTag
