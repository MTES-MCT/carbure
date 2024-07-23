import Form from "common/components/form"
import { NumberInput, TextInput } from "common/components/input"
import { ElecApplicationSample } from "elec-audit-admin/types"
import { useTranslation } from "react-i18next"

const SampleSummary = ({ sample }: { sample?: ElecApplicationSample }) => {
	const { t } = useTranslation()

	return (
		<>
			<strong>Échantillon</strong>

			<Form variant="columns">
				<NumberInput
					readOnly
					label={t("Points de recharge à auditer")}
					value={sample?.charge_points.length}
				/>

				<TextInput
					readOnly
					label={t("Pourcentage de puissance installée à auditeur")}
					value={sample?.percentage + "%"}
				/>
			</Form>
		</>
	)
}

export default SampleSummary
