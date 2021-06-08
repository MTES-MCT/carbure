import { EntitySelection } from "carbure/hooks/use-entity"
import { Main } from "common/components"
import { Section } from "common/components/section"

type StatsProps = {
  entity: EntitySelection
}

const Stats = ({ entity }: StatsProps) => {
  return (
    <Main style={{ padding: "32px 160px" }}>
      <Section>
        <div id="coin" className="list-snapshot_transactionStatus__28gMV" style={ { alignSelf: "center" } }>
          <h1>&#x1F4D6; Vos stats principales &#x1F4D6;</h1>
        </div>
      </Section>
      <Section>
        <iframe
          title="Stats1"
          src={`https://metabase.carbure.beta.gouv.fr/public/dashboard/7aa76cea-b60a-4e89-9bde-a116abd86018?user=${entity?.name}#hide_parameters=user`}
          frameBorder="0"
          width="100%"
          height="420"
          allowTransparency
        />
      </Section>
      <Section>
        <div className="list-snapshot_transactionStatus__28gMV" style={ { alignSelf: "center" } }>
          <h1>&#x1F4C5; Votre dernier mois &#x1F4C5;</h1>
        </div>
      </Section>
      <Section>
        <iframe
          title="Stats2"
          src={`https://metabase.carbure.beta.gouv.fr/public/dashboard/11d88f12-22c4-467a-ad36-f6bf3a924717?user=${entity?.name}#hide_parameters=user`}
          frameBorder="0"
          width="100%"
          height="420"
          allowTransparency
        />
      </Section>
      <Section>
        <div className="list-snapshot_transactionStatus__28gMV" style={ { alignSelf: "center" } }>
          <h1>&#x1F4C8; Vos graphiques &#x1F4C8;</h1>
        </div>
      </Section>
        <span style={ { alignSelf: "center" } }>
          <p><strong>Cliquez </strong>sur une période pour en savoir plus<br/><strong>Choisissez </strong>un biocarburant pour voir ses stats</p>
        </span>
      <Section>
        <iframe
          title="Stats3"
          src={`https://metabase.carbure.beta.gouv.fr/public/dashboard/d3722672-2e9f-48ad-beb0-29c3864b61ab?user=${entity?.name}#hide_parameters=user,biocarb`}
          frameBorder="0"
          width="100%"
          height="690"
          allowTransparency
        />
      </Section>
    </Main>
  )
}

export default Stats
