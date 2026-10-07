import { Main } from "common/components/scaffold"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"

const AdminLotsPage = () => {
  const { t } = useTranslation()
  usePrivateNavigation(t("Lots d'hydrogène"))

  return (
    <Main>
      <header>
        <section>
          <h1>{t("Lots d'hydrogène")}</h1>
        </section>
      </header>
    </Main>
  )
}

export default AdminLotsPage
