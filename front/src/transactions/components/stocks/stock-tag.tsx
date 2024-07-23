import { useTranslation } from "react-i18next"
import { Tag, TagProps, TagVariant } from "common/components/tag"
import { Stock } from "../../types"

export interface StockTagProps extends TagProps {
	stock: Stock
}

export const StockTag = ({ stock, ...props }: StockTagProps) => {
	const { t } = useTranslation()

	let label = t("N/A")
	let variant: TagVariant | undefined = undefined

	if (stock.remaining_volume === stock.initial_volume) {
		variant = "success"
		label = t("En stock")
	} else if (stock.remaining_volume > 0) {
		variant = "info"
		label = t("Entamé")
	} else {
		label = t("Vide")
	}

	return <Tag {...props} variant={variant} label={label} />
}

export default StockTag
