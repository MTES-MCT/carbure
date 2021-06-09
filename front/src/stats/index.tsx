import { EntitySelection } from "carbure/hooks/use-entity"
import { Main } from "common/components"
import { Section } from "common/components/section"
import useAPI from "common/hooks/use-api"
import api from "common/services/api"
import { useEffect } from "react"

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

  return (
    <Main style={{ padding: "32px 160px" }}>
      <Section style={{alignSelf: "center", borderColor: "black", borderRadius: textAngle , borderWidth: textBorderWidth, borderStyle: "solid", width: textWidth}}>
        <div style={{ alignSelf: "center" }}>
          <h1>&#x1F4D6; Vos stats principales &#x1F4D6;</h1>
        </div>
      </Section>
      <Section>
        <iframe
          title="Stats1"
          src={`https://metabase.carbure.beta.gouv.fr/public/dashboard/7aa76cea-b60a-4e89-9bde-a116abd86018?hash=${entityHash.data?.hash}#hide_parameters=hash`}
          frameBorder="0"
          border-radius="100"
          width="100%"
          height="600"
          allowTransparency
        />
      </Section>
      <Section style={{alignSelf: "center", borderColor: "black", borderRadius: textAngle , borderWidth: textBorderWidth, borderStyle: "solid", width: textWidth}}>
        <div style={{ alignSelf: "center" }}>
          <h1>&#x1F4C5; Votre dernier mois &#x1F4C5;</h1>
        </div>
      </Section>
      <Section>
        <iframe
          title="Stats2"
          src={`https://metabase.carbure.beta.gouv.fr/public/dashboard/11d88f12-22c4-467a-ad36-f6bf3a924717?hash=${entityHash.data?.hash}#hide_parameters=hash`}
          frameBorder="0"
          width="100%"
          height="600"
          allowTransparency
        />
      </Section>
      <Section style={{alignSelf: "center", borderColor: "black", borderRadius: textAngle , borderWidth: textBorderWidth, borderStyle: "solid", width: textWidth}}>
        <div style={{ alignSelf: "center" }}>
          <h1>&#x1F4C8; Vos graphiques &#x1F4C8;</h1>
        </div>
      </Section>
        <span style={{alignSelf: "center" }}>
          <p><strong>Choisissez </strong>un biocarburant pour voir ses stats</p>
        </span>
      <Section>
        <iframe
          title="Stats3"
          src={`https://metabase.carbure.beta.gouv.fr/public/dashboard/d3722672-2e9f-48ad-beb0-29c3864b61ab?hash=${entityHash.data?.hash}#hide_parameters=hash,biocarb,matprem`}
          frameBorder="0"
          width="100%"
          height="1700"
          allowTransparency
        />
      </Section>
      <Section style={{alignSelf: "center", borderColor: "black", borderRadius: textAngle , borderWidth: textBorderWidth, borderStyle: "solid", width: textWidth}}>
        <div style={{ alignSelf: "center" }}>
          <h1>&#x1F343; Votre geste écolo &#x1F343;</h1>
        </div>
      </Section>
      <Section>
        <iframe
          title="Stats4"
          src={`https://metabase.carbure.beta.gouv.fr/public/dashboard/a960a32f-c14f-4835-9f6f-2553e951620c?hash=${entityHash.data?.hash}#hide_parameters=hash`}
          frameBorder="0"
          width="100%"
          height="600"
          allowTransparency
        />
      </Section>
    </Main>
  )
}

export default Stats
