import { Route, Routes } from "react-router-dom"
import { Trans, useTranslation } from "react-i18next"
import IframeResizer from "iframe-resizer-react"
import { LoaderOverlay, Main, Panel } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import api, { Api } from "common/services/api"
import { Entity, EntityType } from "carbure/types"
import useTitle from "common/hooks/title"
import useEntity from "carbure/hooks/entity"
import { getEntityStats } from "./api"

const Stats = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  useTitle(t("Statistiques") + " " + entity.name)

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
          <Trans>{t("Statistiques")}</Trans>
        </h1>
      </header>
      <section>
        <IframeResizer
          src={statsData?.metabase_iframe_url}
          frameBorder="0"
          allowTransparency
          style={{ boxShadow: "var(--shadow)" }}
        />
      </section>
    </Main>
  )
}

export default Stats
