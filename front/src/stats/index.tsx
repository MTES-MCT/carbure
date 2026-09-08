import { useTranslation } from "react-i18next"
import { LoaderOverlay, Main } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import useTitle from "common/hooks/title"
import useEntity from "common/hooks/entity"
import { getEntityStats } from "./api"
import { usePrivateNavigation } from "common/layouts/navigation"
import { MetabaseIframe } from "common/molecules/metabase-iframe"

const Stats = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  useTitle(t("Statistiques") + " " + entity.name)
  usePrivateNavigation(t("Statistiques"))

  const statsResponse = useQuery(getEntityStats, {
    key: "entities",
    params: [entity.id],
  })

  const statsData = statsResponse.result

  return !statsData?.metabase_iframe_url ? (
    <LoaderOverlay />
  ) : (
    <Main>
      <section>
        <MetabaseIframe src={statsData.metabase_iframe_url} />
      </section>
    </Main>
  )
}

export default Stats
