import { useTranslation } from "react-i18next"
import Button from "common/components/button"
import { Plus } from "common/components/icons"

export const CreateButton = () => {
	const { t } = useTranslation()
	return (
		<Button variant="primary" icon={Plus} label={t("Créer un lot")} to="#add" />
	)
}
