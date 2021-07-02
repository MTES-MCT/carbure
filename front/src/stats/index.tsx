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
  return api.get('/settings/entity-hash', {entity_id: entityId})
}

type StatsProps = {
  entity: EntitySelection
}

const Stats = ({ entity }: StatsProps) => {
  const [entityHash, getEntityHash] = useAPI(getHash);
  useEffect (() => {
    if (entity) {
      getEntityHash(entity.id);
    }
  },[entity,getEntityHash])

  const { t } = useTranslation()

  if (entityHash.data === null) {
    return null;
  } 

  const textWidth = 550
  const textAngle = 15
  const textBorderWidth = 2
  const textColor = "black"
  const textShadow = "6px 6px 3px grey"
  const iframeShadow = "1px 1px 6px grey"
  let entityTypeLink = "NA"
  let entityTypeTitle = ""

  
  if(entity?.entity_type === EntityType.Operator) {
    entityTypeLink = `https://metabase.carbure.beta.gouv.fr/public/dashboard/e7f0eacb-1034-4173-8634-ec4e000cd027?hash=${entityHash.data?.hash}#hide_parameters=hash`
    entityTypeTitle = t("En savoir plus sur vos fournisseurs")

  } else if(entity?.entity_type === EntityType.Producer) {
    entityTypeLink = `https://metabase.carbure.beta.gouv.fr/public/dashboard/765ad219-d854-40e9-8f78-e32dedd28c54?hash=${entityHash.data?.hash}#hide_parameters=hash`
    entityTypeTitle = t("En savoir plus sur vos clients")
    
  } else if(entity?.entity_type === EntityType.Trader) {
    entityTypeLink = `https://metabase.carbure.beta.gouv.fr/public/dashboard/8d1e621d-f005-4904-a19d-e74305d3ce14?hash=${entityHash.data?.hash}#hide_parameters=hash`
    entityTypeTitle = t("En savoir plus sur vos clients et vos fournisseurs")
  }

  return (
    <Main style={{padding: "32px 120px"}}>
      <Section style={{boxShadow: textShadow, alignSelf: "center", borderColor:textColor, borderRadius: textAngle , borderWidth: textBorderWidth, borderStyle: "solid", width: textWidth}}>
        <div style={{ alignSelf: "center" }}>
          <h1>
            <a style={{color:textColor}} href={`https://metabase.carbure.beta.gouv.fr/public/dashboard/a960a32f-c14f-4835-9f6f-2553e951620c?hash=${entityHash.data?.hash}#hide_parameters=hash`}>
              <Trans>&#x1F30D; Votre empreinte carbone &#x1F30D;</Trans>
            </a>
          </h1>
        </div>
      </Section>
      <Section style={{boxShadow: iframeShadow}}>
        <IframeResizer
          title="Votre empreinte carbone"
          src={`https://metabase.carbure.beta.gouv.fr/public/dashboard/a960a32f-c14f-4835-9f6f-2553e951620c?hash=${entityHash.data?.hash}#hide_parameters=hash`}
          frameBorder="0"
          allowTransparency
        />
      </Section>
      <Section style={{boxShadow: textShadow, alignSelf: "center", borderColor: textColor, borderRadius: textAngle , borderWidth: textBorderWidth, borderStyle: "solid", width: textWidth}}>
        <div style={{ alignSelf: "center" }}>
          <h1>
            <a style={{color:textColor}} href={`https://metabase.carbure.beta.gouv.fr/public/dashboard/7aa76cea-b60a-4e89-9bde-a116abd86018?hash=${entityHash.data?.hash}#hide_parameters=hash`}>
              <Trans>&#x1F4D6; Statistiques globales depuis 2019 &#x1F4D6;</Trans>
            </a>
          </h1>
        </div>
      </Section>
      <Section style={{boxShadow: iframeShadow}}>
        <IframeResizer
          title="Statistiques globales depuis 2019"
          src={`https://metabase.carbure.beta.gouv.fr/public/dashboard/7aa76cea-b60a-4e89-9bde-a116abd86018?hash=${entityHash.data?.hash}#hide_parameters=hash`}
          frameBorder="0"
          allowTransparency
        />
      </Section>
      <Section style={{boxShadow: textShadow, alignSelf: "center", borderColor: textColor, borderRadius: textAngle , borderWidth: textBorderWidth, borderStyle: "solid", width: textWidth}}>
        <div style={{ alignSelf: "center" }}>
          <h1>
            <a style={{color:textColor}} href={`https://metabase.carbure.beta.gouv.fr/public/dashboard/11d88f12-22c4-467a-ad36-f6bf3a924717?hash=${entityHash.data?.hash}#hide_parameters=hash`}>
              <Trans>&#x1F4C5; Le mois dernier &#x1F4C5;</Trans>
            </a>
          </h1>
        </div>
      </Section>
      <Section style={{boxShadow: iframeShadow}}>
        <IframeResizer
          title="Le mois dernier"
          src={`https://metabase.carbure.beta.gouv.fr/public/dashboard/11d88f12-22c4-467a-ad36-f6bf3a924717?hash=${entityHash.data?.hash}#hide_parameters=hash`}
          frameBorder="0"
          allowTransparency
        />
      </Section>
      <Section style={{boxShadow: textShadow, alignSelf: "center", borderColor: textColor, borderRadius: textAngle , borderWidth: textBorderWidth, borderStyle: "solid", width: textWidth}}>
        <div style={{ alignSelf: "center" }}>
          <h1>
            <a style={{color:textColor}} href={`https://metabase.carbure.beta.gouv.fr/public/dashboard/e3b75456-7df2-4afe-89ea-ac9601abe349?hash=${entityHash.data?.hash}#hide_parameters=hash`}>
              <Trans>&#x231B; Statistiques globales par année &#x231B;</Trans>
            </a>
          </h1>
        </div>
      </Section>
      <Section style={{background:"#d9edf7", borderColor:"#bce8f1"}}>
        <span style={{alignSelf: "center" }}>
          <Trans><p><b>Choisissez</b> une année qui vous intéresse dans le sélecteur</p></Trans>
        </span>
      </Section>
      <Section>
        <IframeResizer
          title="Statistiques globale par année"
          src={`https://metabase.carbure.beta.gouv.fr/public/dashboard/e3b75456-7df2-4afe-89ea-ac9601abe349?hash=${entityHash.data?.hash}#hide_parameters=hash`}
          frameBorder="0"
          allowTransparency
        />
      </Section>
      <Section style={{boxShadow: textShadow, alignSelf: "center", borderColor: textColor, borderRadius: textAngle , borderWidth: textBorderWidth, borderStyle: "solid", width: textWidth}}>
        <div style={{ alignSelf: "center" }}>
          <h1>
            <a style={{color:textColor}} href={`https://metabase.carbure.beta.gouv.fr/public/dashboard/d3722672-2e9f-48ad-beb0-29c3864b61ab?hash=${entityHash.data?.hash}#hide_parameters=hash,biocarb,matprem`}>
              <Trans>&#x1F4C8; Statistiques détaillées &#x1F4C8;</Trans>
            </a>
          </h1>
        </div>
      </Section>
      <Section style={{background:"#d9edf7", borderColor:"#bce8f1"}}>
        <span style={{alignSelf: "center" }}>
          <Trans><p><b>Cliquez</b> sur une année, un biocarburant ou une matière première pour afficher les détails</p></Trans>
        </span>
      </Section>
      <Section style={{boxShadow: iframeShadow}}>
        <IframeResizer
          title="Statistiques détaillées"
          src={`https://metabase.carbure.beta.gouv.fr/public/dashboard/d3722672-2e9f-48ad-beb0-29c3864b61ab?hash=${entityHash.data?.hash}#hide_parameters=hash,biocarb,matprem`}
          frameBorder="0"
          allowTransparency
        />
      </Section>
      <Section style={{boxShadow: textShadow, alignSelf: "center", borderColor: textColor, borderRadius: textAngle , borderWidth: textBorderWidth, borderStyle: "solid", width: textWidth * 1.3}}>
        <div style={{ alignSelf: "center" }}>
          <h1>
            <a style={{color:textColor}} href={entityTypeLink}>
              &#9981; {entityTypeTitle} &#9981;
            </a>
          </h1>
        </div>
      </Section>
      <Section style={{boxShadow: iframeShadow}}>
        <IframeResizer
          title = {entityTypeTitle}
          src={entityTypeLink}
          frameBorder="0"
          allowTransparency
        />
      </Section>
    </Main>
  )
}

const StatsRoutes = ({ entity }: StatsProps) => {
  const [entityHash, getEntityHash] = useAPI(getHash);
  useEffect (() => {
    if (entity) {
      getEntityHash(entity.id);
    }
  },[entity,getEntityHash])

  if (entityHash.data === null) {
    return null;
  }

  const path = window.location.pathname
  const period = path.substring(32,39)
  const iframeShadow = "1px 1px 6px grey"
  return ( 
    <Switch>
      <Route relative exact path="">
        <Stats entity={entity} />
      </Route>

      <Route relative exact path="period_details">
        <Main style={{ padding: "32px 160px" }}>
          <h1>{period}</h1>
          <Section style={{boxShadow: iframeShadow}}>
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
