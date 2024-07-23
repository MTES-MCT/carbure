import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Map } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { toSearchParams } from "common/services/api"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { LotQuery } from "transactions/types"

interface DeliveryMapButtonProps {
	query: LotQuery
}

const DeliveryMapButton = ({ query }: DeliveryMapButtonProps) => {
	const { t } = useTranslation()
	const portal = usePortal()
	return (
		<Button
			icon={Map}
			label={t("Voir la carte des livraisons")}
			action={() =>
				portal((close) => <DeliveryMapDialog query={query} onClose={close} />)
			}
		/>
	)
}

interface DeliveryMapDialogProps {
	query: LotQuery
	onClose: () => void
}

const DeliveryMapDialog = ({ query, onClose }: DeliveryMapDialogProps) => {
	const { t } = useTranslation()

	const [loading, setLoading] = useState(true)

	// prepare query params for current search
	const searchParams = toSearchParams({
		...query,
		limit: undefined,
		from_idx: undefined,
	}).toString()

	return (
		<Dialog onClose={onClose} style={{ width: "100%" }}>
			<iframe
				title={t("Carte des livraisons")}
				src={`/api/transactions/admin/flow-map?${searchParams}`}
				frameBorder="0"
				style={{ width: "1px", minWidth: "100%", overflow: "hidden" }}
				onLoad={(e) => {
					const iframe = e.target as HTMLIFrameElement
					const doc = iframe.contentDocument
					const last = doc?.querySelector("body *:last-child")

					if (last) {
						iframe.height = last.getBoundingClientRect().bottom + "px"
						setLoading(false)
					}
				}}
			/>
			{loading && <LoaderOverlay />}
		</Dialog>
	)
}

export default DeliveryMapButton
