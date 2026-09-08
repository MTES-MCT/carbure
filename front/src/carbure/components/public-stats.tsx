import { useTranslation } from "react-i18next"
import { MetabaseIframe } from "common/molecules/metabase-iframe"
import { Main } from "common/components/scaffold"
import useTitle from "common/hooks/title"
import { usePrivateNavigation } from "common/layouts/navigation"

const currentYear = new Date().getFullYear()

const PublicStats = () => {
  const { t } = useTranslation()
  useTitle(t("Statistiques publiques"))
  usePrivateNavigation(t("Statistiques publiques"))

  const publicLink =
    "https://metabase.carbure.beta.gouv.fr/public/dashboard/7850c353-c225-4b51-9181-6e45f59ea3ba"

  return (
    <Main>
      <section>
        <MetabaseIframe
          src={`${publicLink}?annee=${currentYear}#hide_parameters=annee`}
        />
      </section>
    </Main>
  )
}

export default PublicStats
