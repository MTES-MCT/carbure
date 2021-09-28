import { Main } from "common/components"
import { EntitySelection } from "carbure/hooks/use-entity"
import AgreementList from "./components/agreement-list"

type DoubleCountingProps = {
  entity: EntitySelection
}

const DoubleCounting = ({ entity }: DoubleCountingProps) => {
  return (
    <Main>
      <AgreementList entity={entity} />
    </Main>
  )
}

export default DoubleCounting
