import { useTranslation } from "react-i18next"
import { Main } from "common/components/scaffold"
import useTitle from "common/hooks/title"
import Declarations from "./components/declarations"

const Dashboard = () => {
	useTitle("Administration")
	const { t } = useTranslation()

	return (
		<Main>
			<header>
				<h1>{t("Tableau de bord")}</h1>
			</header>

			<section>
				<Declarations />
			</section>
		</Main>
	)
}

export default Dashboard
