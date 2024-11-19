import { useTranslation } from "react-i18next"
import { Main } from "common/components/scaffold"
import useTitle from "common/hooks/title"
import Declarations from "./components/declarations"
import { usePrivateNavigation } from "common/layouts/navigation"

const Dashboard = () => {
  const { t } = useTranslation()

  useTitle("Administration")
  usePrivateNavigation(t("Tableau de bord"))

  return (
    <Main>
      <Declarations />
    </Main>
  )
}

export default Dashboard
