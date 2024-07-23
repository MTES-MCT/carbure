import { InfoCircle } from "common/components/icons"
import Tooltip from "common/components/tooltip"
import { t } from "i18next"
import { Trans } from "react-i18next"
import { DoubleCountingFileInfo } from "../../../double-counting/types"

const FileApplicationInfo = ({
	fileData,
}: {
	fileData: DoubleCountingFileInfo
}) => {
	return (
		<section>
			<p>
				<Trans
					values={{
						productionSite: fileData.production_site,
					}}
					defaults={`Pour le site de production <b>{{productionSite}}</b> par `}
				/>
				<a href={`mailto:${fileData.producer_email}`}>
					{fileData.producer_email}
				</a>
				.
			</p>
			<p>
				<Trans
					values={{
						fileName: fileData.file_name,
					}}
					defaults="Fichier excel téléchargé : <b>{{fileName}}</b>"
				/>
			</p>
			<p>
				<Tooltip
					title={t(
						`L'année détectée est renseignée en bas de l'onglet "Reconnaissance double comptage" du fichier excel.`
					)}
				>
					<Trans
						values={{
							period: fileData.start_year
								? `${fileData.start_year} - ${fileData.start_year + 1}`
								: t("Non reconnue"),
						}}
						defaults="Période demandée : <b>{{ period }}</b>"
					/>
					<InfoCircle
						color="#a4a4a4"
						size={15}
						style={{
							margin: "0px 0px 0 2px",
							position: "relative",
							top: "2px",
						}}
					/>
				</Tooltip>
			</p>
		</section>
	)
}
export default FileApplicationInfo
