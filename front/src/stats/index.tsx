import { Route, Switch, Link } from "common/components/relative-route"
import { EntitySelection } from "carbure/hooks/use-entity"
import { Trans, useTranslation } from "react-i18next"
import { Main } from "common/components"
import { Section } from "common/components/section"
import IframeResizer from "iframe-resizer-react"
import useAPI from "common/hooks/use-api"
import api from "common/services/api"
import { useEffect } from "react"
import { EntityType } from "common/types"

function getHash(entityId: number) {
  return api.get("/settings/entity-hash", { entity_id: entityId })
}

type StatsProps = {
  entity: EntitySelection
}

const Stats = ({ entity }: StatsProps) => {
  const [entityHash, getEntityHash] = useAPI(getHash)
  useEffect(() => {
    if (entity) {
      getEntityHash(entity.id)
    }
  }, [entity, getEntityHash])

  const { t } = useTranslation()

  if (entityHash.data === null) {
    return null
  }

  const textWidth = 550
  const textAngle = 15
  const textBorderWidth = 2
  const textColor = "black"
  const textShadow = "6px 6px 3px grey"
  const iframeShadow = "1px 1px 6px grey"
  let link1 = ""
  let link2 = ""
  let link3 = ""
  let link4 = ""
  let link5 = ""
  let link6 = "NA"
  let text6 = ""

  if (entity?.entity_type === EntityType.Operator) {
    link1 = `https://metabase.carbure.beta.gouv.fr/public/dashboard/4fe4f013-188e-4693-81ec-963daeb758eb?hash=${entityHash.data?.hash}#hide_parameters=hash`
    link2 = `https://metabase.carbure.beta.gouv.fr/public/dashboard/f184cea4-967a-4284-902c-4a87acff5ca2?hash=${entityHash.data?.hash}#hide_parameters=hash`
    link3 = `https://metabase.carbure.beta.gouv.fr/public/dashboard/04601b75-225a-4a51-9491-9c9f40544f3e?hash=${entityHash.data?.hash}#hide_parameters=hash`
    link4 = `https://metabase.carbure.beta.gouv.fr/public/dashboard/2a697167-ddee-4fdf-aa59-43c981c71b53?hash=${entityHash.data?.hash}#hide_parameters=hash`
    link5 = `https://metabase.carbure.beta.gouv.fr/public/dashboard/2a481cb9-8db9-4ef3-bb05-4721c0a9d497?hash=${entityHash.data?.hash}#hide_parameters=hash`
    link6 = `https://metabase.carbure.beta.gouv.fr/public/dashboard/e7f0eacb-1034-4173-8634-ec4e000cd027?hash=${entityHash.data?.hash}#hide_parameters=hash`
    text6 = t("En savoir plus sur vos fournisseurs")
  } else if (entity?.entity_type === EntityType.Producer) {
    link1 = `https://metabase.carbure.beta.gouv.fr/public/dashboard/a960a32f-c14f-4835-9f6f-2553e951620c?hash=${entityHash.data?.hash}#hide_parameters=hash`
    link2 = `https://metabase.carbure.beta.gouv.fr/public/dashboard/7aa76cea-b60a-4e89-9bde-a116abd86018?hash=${entityHash.data?.hash}#hide_parameters=hash`
    link3 = `https://metabase.carbure.beta.gouv.fr/public/dashboard/11d88f12-22c4-467a-ad36-f6bf3a924717?hash=${entityHash.data?.hash}#hide_parameters=hash`
    link4 = `https://metabase.carbure.beta.gouv.fr/public/dashboard/e3b75456-7df2-4afe-89ea-ac9601abe349?hash=${entityHash.data?.hash}#hide_parameters=hash`
    link5 = `https://metabase.carbure.beta.gouv.fr/public/dashboard/d3722672-2e9f-48ad-beb0-29c3864b61ab?hash=${entityHash.data?.hash}#hide_parameters=hash`
    link6 = `https://metabase.carbure.beta.gouv.fr/public/dashboard/765ad219-d854-40e9-8f78-e32dedd28c54?hash=${entityHash.data?.hash}#hide_parameters=hash`
    text6 = t("En savoir plus sur vos clients")
  } else if (entity?.entity_type === EntityType.Trader) {
    link1 = `https://metabase.carbure.beta.gouv.fr/public/dashboard/a960a32f-c14f-4835-9f6f-2553e951620c?hash=${entityHash.data?.hash}#hide_parameters=hash`
    link2 = `https://metabase.carbure.beta.gouv.fr/public/dashboard/f87e0e09-f82f-4ed1-82c6-2a8d85a1a8e3?hash=${entityHash.data?.hash}#hide_parameters=hash`
    link3 = `https://metabase.carbure.beta.gouv.fr/public/dashboard/801e5d6c-fb19-4f4c-82bb-06a7d0c7e5a8?hash=${entityHash.data?.hash}#hide_parameters=hash`
    link4 = `https://metabase.carbure.beta.gouv.fr/public/dashboard/8eb16042-a39e-469a-b357-10bcb3c4190d?hash=${entityHash.data?.hash}#hide_parameters=hash`
    link5 = `https://metabase.carbure.beta.gouv.fr/public/dashboard/70adcd33-801b-4ec4-a135-8cc5d33a6306?hash=${entityHash.data?.hash}#hide_parameters=hash`
    link6 = `https://metabase.carbure.beta.gouv.fr/public/dashboard/8d1e621d-f005-4904-a19d-e74305d3ce14?hash=${entityHash.data?.hash}#hide_parameters=hash`
    text6 = t("En savoir plus sur vos clients et vos fournisseurs")
  } else {
    link6 = `about:blank`
    text6 = "Error"
  }

  return (
    <Main style={{ padding: "32px var(--main-spacing)" }}>
      <Section
        style={{
          boxShadow: textShadow,
          alignSelf: "center",
          borderColor: textColor,
          borderRadius: textAngle,
          borderWidth: textBorderWidth,
          borderStyle: "solid",
          width: textWidth,
        }}
      >
        <div style={{ alignSelf: "center" }}>
          <h1>
            <a style={{ color: textColor }} href={link1}>
              &#x1F30D; <Trans>Votre empreinte carbone</Trans> &#x1F30D;
            </a>
          </h1>
        </div>
      </Section>
      <Section style={{ boxShadow: iframeShadow }}>
        <IframeResizer
          title="Votre empreinte carbone"
          src={link1}
          frameBorder="0"
          allowTransparency
        />
      </Section>
      <Section
        style={{
          boxShadow: textShadow,
          alignSelf: "center",
          borderColor: textColor,
          borderRadius: textAngle,
          borderWidth: textBorderWidth,
          borderStyle: "solid",
          width: textWidth,
        }}
      >
        <div style={{ alignSelf: "center" }}>
          <h1>
            <a style={{ color: textColor }} href={link2}>
              &#x1F4D6; <Trans>Statistiques globales depuis 2019</Trans>{" "}
              &#x1F4D6;
            </a>
          </h1>
        </div>
      </Section>
      <Section style={{ boxShadow: iframeShadow }}>
        <IframeResizer
          title="Statistiques globales depuis 2019"
          src={link2}
          frameBorder="0"
          allowTransparency
        />
      </Section>
      <Section
        style={{
          boxShadow: textShadow,
          alignSelf: "center",
          borderColor: textColor,
          borderRadius: textAngle,
          borderWidth: textBorderWidth,
          borderStyle: "solid",
          width: textWidth,
        }}
      >
        <div style={{ alignSelf: "center" }}>
          <h1>
            <a style={{ color: textColor }} href={link3}>
              &#x1F4C5; <Trans>Le mois dernier</Trans> &#x1F4C5;
            </a>
          </h1>
        </div>
      </Section>
      <Section style={{ boxShadow: iframeShadow }}>
        <IframeResizer
          title="Le mois dernier"
          src={link3}
          frameBorder="0"
          allowTransparency
        />
      </Section>
      <Section
        style={{
          boxShadow: textShadow,
          alignSelf: "center",
          borderColor: textColor,
          borderRadius: textAngle,
          borderWidth: textBorderWidth,
          borderStyle: "solid",
          width: textWidth,
        }}
      >
        <div style={{ alignSelf: "center" }}>
          <h1>
            <a style={{ color: textColor }} href={link4}>
              &#x231B; <Trans>Statistiques globales par année</Trans> &#x231B;
            </a>
          </h1>
        </div>
      </Section>
      <Section style={{ background: "#d9edf7", borderColor: "#bce8f1" }}>
        <span style={{ alignSelf: "center" }}>
          <Trans>
            <p>
              <b>Choisissez</b> une année qui vous intéresse dans le sélecteur
            </p>
          </Trans>
        </span>
      </Section>
      <Section>
        <IframeResizer
          title="Statistiques globale par année"
          src={link4}
          frameBorder="0"
          allowTransparency
        />
      </Section>
      <Section
        style={{
          boxShadow: textShadow,
          alignSelf: "center",
          borderColor: textColor,
          borderRadius: textAngle,
          borderWidth: textBorderWidth,
          borderStyle: "solid",
          width: textWidth,
        }}
      >
        <div style={{ alignSelf: "center" }}>
          <h1>
            <a style={{ color: textColor }} href={link5}>
              &#x1F4C8; <Trans>Statistiques détaillées</Trans> &#x1F4C8;
            </a>
          </h1>
        </div>
      </Section>
      <Section style={{ background: "#d9edf7", borderColor: "#bce8f1" }}>
        <span style={{ alignSelf: "center" }}>
          <Trans>
            <p>
              <b>Choisissez</b> une année, un biocarburant ou une matière
              première dans le sélecteur pour afficher les détails
            </p>
          </Trans>
        </span>
      </Section>
      <Section style={{ boxShadow: iframeShadow }}>
        <IframeResizer
          title="Statistiques détaillées"
          src={link5}
          frameBorder="0"
          allowTransparency
        />
      </Section>
      <Section
        style={{
          boxShadow: textShadow,
          alignSelf: "center",
          borderColor: textColor,
          borderRadius: textAngle,
          borderWidth: textBorderWidth,
          borderStyle: "solid",
          width: textWidth * 1.3,
        }}
      >
        <div style={{ alignSelf: "center" }}>
          <h1>
            <a style={{ color: textColor }} href={link6}>
              &#9981; {text6} &#9981;
            </a>
          </h1>
        </div>
      </Section>
      <Section style={{ boxShadow: iframeShadow }}>
        <IframeResizer
          title={text6}
          src={link6}
          frameBorder="0"
          allowTransparency
        />
      </Section>
    </Main>
  )
}

const StatsRoutes = ({ entity }: StatsProps) => {
  const [entityHash, getEntityHash] = useAPI(getHash)
  useEffect(() => {
    if (entity) {
      getEntityHash(entity.id)
    }
  }, [entity, getEntityHash])

  if (entityHash.data === null) {
    return null
  }

  const path = window.location.pathname
  const period = path.substring(32, 39)
  const iframeShadow = "1px 1px 6px grey"
  return (
    <Switch>
      <Route relative exact path="">
        <Stats entity={entity} />
      </Route>

      <Route relative exact path="period_details">
        <Main style={{ padding: "32px 160px" }}>
          <h1>{period}</h1>
          <Section style={{ boxShadow: iframeShadow }}>
            <IframeResizer
              title="period_details"
              src={`https://metabase.carbure.beta.gouv.fr/public/dashboard/8d158d55-0adf-41e2-b711-6f8e0419b824?hash=${entityHash.data?.hash},period=${period}#hide_parameters=hash,period`}
              frameBorder="0"
              allowTransparency
            />
          </Section>
        </Main>
      </Route>
    </Switch>
  )
}

export default StatsRoutes
