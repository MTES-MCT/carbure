import { useTranslation } from "react-i18next"
import { UserRightRequest } from "carbure/types"
import { usePortal } from "common/components/portal"
import Button from "common/components/button"
import { Cross } from "common/components/icons"
import { Confirm } from "common/components/dialog"

type RejectUserButtonProps = {
	onRejectUser: () => void
	request: UserRightRequest
}

export const RejectUserButton = ({
	request,
	onRejectUser,
}: RejectUserButtonProps) => {
	const { t } = useTranslation()
	const portal = usePortal()

	const user = request.user[0]

	return (
		<Button
			captive
			variant="icon"
			icon={Cross}
			title={t("Refuser")}
			action={() =>
				portal((close) => (
					<Confirm
						title={t("Refuser un utilisateur")}
						description={t("Voulez vous refuser l'accès à votre société à {{user}} ?", { user })} // prettier-ignore
						confirm={t("Refuser")}
						icon={Cross}
						variant="danger"
						onConfirm={() => Promise.resolve(onRejectUser())}
						onClose={close}
					/>
				))
			}
		/>
	)
}
