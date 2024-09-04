import { Trans, useTranslation } from "react-i18next"
import IframeResizer from "iframe-resizer-react"
import { LoaderOverlay, Main } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import useTitle from "common/hooks/title"
import useEntity from "carbure/hooks/entity"
import { getEntityStats } from "./api"
import { Loader } from "common/components/icons"
import { useState } from "react"

const Stats = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  useTitle(t("Statistiques") + " " + entity.name)
  const [isLoaded, setIsLoaded] = useState(false)

  const statsResponse = useQuery(getEntityStats, {
    key: "entities",
    params: [entity.id],
  })

  const statsData = statsResponse.result

  return !statsData?.metabase_iframe_url ? (
    <LoaderOverlay />
  ) : (
    <Main>
      <header>
        <h1>
          <Trans>Statistiques</Trans>
        </h1>
      </header>
      <section>
        <IframeResizer
          onResized={() => setIsLoaded(true)}
          src={statsData?.metabase_iframe_url}
          frameBorder="0"
          allowTransparency
          style={{ boxShadow: "var(--shadow)" }}
        />
      </section>
      {!isLoaded && (
        <section style={{ alignItems: "center" }}>
          {" "}
          <Loader color="var(--black)" size={32} />
        </section>
      )}
    </Main>
  )
}

export default Stats
