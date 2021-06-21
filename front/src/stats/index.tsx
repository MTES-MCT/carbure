import { Route, Switch, Link } from "common/components/relative-route"
import { EntitySelection } from "carbure/hooks/use-entity"
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

  if (entityHash.data === null) {
    return null;
  }

  const textWidth = 420
  const textAngle = 15
  const textBorderWidth = 2
  const textShadow = "6px 6px 3px grey"
  const iframeShadow = "1px 1px 6px grey"

  if(entity?.entity_type === EntityType.Operator) {
  return (
    <Main style={{padding: "32px 120px"}}>
      <Section style={{boxShadow: textShadow, alignSelf: "center", borderColor: "black", borderRadius: textAngle , borderWidth: textBorderWidth, borderStyle: "solid", width: textWidth}}>
        <div style={{ alignSelf: "center" }}>
            <h1>
              <a href={`https://metabase.carbure.beta.gouv.fr/public/dashboard/7aa76cea-b60a-4e89-9bde-a116abd86018?hash=${entityHash.data?.hash}#hide_parameters=hash`}>
                &#x1F4D6; Vos stats principales &#x1F4D6;
              </a>
            </h1>
        </div>
      </Section>
      <Section style={{boxShadow: iframeShadow}}>
        <IframeResizer
          title="Stats1"
          src={`https://metabase.carbure.beta.gouv.fr/public/dashboard/7aa76cea-b60a-4e89-9bde-a116abd86018?hash=${entityHash.data?.hash}#hide_parameters=hash`}
          frameBorder="0"
          allowTransparency
        />
      </Section>
      <Section style={{boxShadow: textShadow, alignSelf: "center", borderColor: "black", borderRadius: textAngle , borderWidth: textBorderWidth, borderStyle: "solid", width: textWidth}}>
        <div style={{ alignSelf: "center" }}>
          <h1>
            <a href={`https://metabase.carbure.beta.gouv.fr/public/dashboard/11d88f12-22c4-467a-ad36-f6bf3a924717?hash=${entityHash.data?.hash}#hide_parameters=hash`}>
              &#x1F4C5; Votre dernier mois &#x1F4C5;
            </a>
          </h1>
        </div>
      </Section>
      <Section style={{boxShadow: iframeShadow}}>
        <IframeResizer
          title="Stats2"
          src={`https://metabase.carbure.beta.gouv.fr/public/dashboard/11d88f12-22c4-467a-ad36-f6bf3a924717?hash=${entityHash.data?.hash}#hide_parameters=hash`}
          frameBorder="0"
          allowTransparency
        />
      </Section>
      <Section style={{boxShadow: textShadow, alignSelf: "center", borderColor: "black", borderRadius: textAngle , borderWidth: textBorderWidth, borderStyle: "solid", width: textWidth}}>
        <div style={{ alignSelf: "center" }}>
          <h1>
            <a href={`https://metabase.carbure.beta.gouv.fr/public/dashboard/d3722672-2e9f-48ad-beb0-29c3864b61ab?hash=${entityHash.data?.hash}#hide_parameters=hash,biocarb,matprem`}>
              &#x1F4C8; Vos graphiques &#x1F4C8;
            </a>
          </h1>
        </div>
      </Section>
      <Section style={{background:"#d9edf7", borderColor:"#bce8f1"}}>
        <span style={{alignSelf: "center" }}>
          <p><b>Choisissez</b> un biocarburant ou une matière première pour voir ses stats</p>
        </span>
      </Section>
      <Section style={{boxShadow: iframeShadow}}>
        <IframeResizer
          title="Stats3"
          src={`https://metabase.carbure.beta.gouv.fr/public/dashboard/d3722672-2e9f-48ad-beb0-29c3864b61ab?hash=${entityHash.data?.hash}#hide_parameters=hash,biocarb,matprem`}
          frameBorder="0"
          allowTransparency
        />
      </Section>
      <Section style={{boxShadow: textShadow, alignSelf: "center", borderColor: "black", borderRadius: textAngle , borderWidth: textBorderWidth, borderStyle: "solid", width: textWidth}}>
        <div style={{ alignSelf: "center" }}>
          <h1>
            <a href={`https://metabase.carbure.beta.gouv.fr/public/dashboard/a960a32f-c14f-4835-9f6f-2553e951620c?hash=${entityHash.data?.hash}#hide_parameters=hash`}>
              &#x1F343; Votre empreinte carbone &#x1F343;
            </a>
          </h1>
        </div>
      </Section>
      <Section style={{boxShadow: iframeShadow}}>
        <IframeResizer
          title="Stats4"
          src={`https://metabase.carbure.beta.gouv.fr/public/dashboard/a960a32f-c14f-4835-9f6f-2553e951620c?hash=${entityHash.data?.hash}#hide_parameters=hash`}
          frameBorder="0"
          allowTransparency
        />
      </Section>
    </Main>
  )
  } else if(entity?.entity_type === EntityType.Producer) {
      return <h1>JeSuisProducteur</h1>
  } else {
      return null
  }
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

  return ( 
    <Switch>
      <Route relative exact path="">
        <Stats entity={entity} />
      </Route>

      <Route relative exact path="period_details">
        <Main style={{ padding: "32px 160px" }}>
          <h1>{period}</h1>
          <Section style={{alignSelf: "center"}}>
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
