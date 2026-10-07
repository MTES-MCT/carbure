import { Main } from "common/components/scaffold"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"

const AdminCertificatesPage = () => {
  const { t } = useTranslation()
  usePrivateNavigation(t("Certificats d'hydrogène"))

  return (
    <Main>
      <header>
        <section>
          <h1>{t("Certificats d'hydrogène")}</h1>
        </section>
      </header>
    </Main>
  )
}

export default AdminCertificatesPage
