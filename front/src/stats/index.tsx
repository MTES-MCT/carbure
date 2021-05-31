import { EntitySelection } from "carbure/hooks/use-entity"
import { Main } from "common/components"
import { Section } from "common/components/section"

type StatsProps = {
  entity: EntitySelection
}

const Stats = ({ entity }: StatsProps) => {
  return (
    <Main style={{ padding: "32px 120px" }}>
      <Section>
        <iframe
          title="stats"
          src={`https://metabase.carbure.beta.gouv.fr/public/dashboard/e3e1e7e4-5b8b-4d0a-8df1-c6d02e8b0fc7?user=${entity?.name}#hide_parameters=user`}
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
