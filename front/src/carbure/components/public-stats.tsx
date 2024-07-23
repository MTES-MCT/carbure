import { Main } from "common/components/scaffold"
import useTitle from "common/hooks/title"
import IframeResizer from "iframe-resizer-react"
import { useTranslation } from "react-i18next"

const currentYear = new Date().getFullYear()

const PublicStats = () => {
	const { t } = useTranslation()
	useTitle(t("Statistiques publiques"))

	const publicLink =
		"https://metabase.carbure.beta.gouv.fr/public/dashboard/7850c353-c225-4b51-9181-6e45f59ea3ba"

	return (
		<Main>
			<section>
				<IframeResizer
					src={`${publicLink}?annee=${currentYear}#hide_parameters=annee`}
					frameBorder="0"
					allowTransparency
					style={{ boxShadow: "var(--shadow)" }}
				/>
			</section>
		</Main>
	)
}

export default PublicStats
