import { Entity, EntityType } from "common/types"
import { Main } from "common/components"
import { Section } from "common/components/section"
import Topbar from "carbure/components/top-bar"
import Footer from "carbure/components/footer"
import Settings from "settings"
import Entities from "../entities" // not using relative path prevents import
import { EntitySelection } from "carbure/hooks/use-entity"
import { AppHook } from "carbure/hooks/use-app"

// check if a given entity can have access to the tirib page
export function hasTirib(entity: Entity | null): boolean {
  if (entity === null) return false
  else if (entity.entity_type === EntityType.Operator) return true
  else if (entity.has_mac) return true
  else return false
}

type TiribProps = {
  entity: EntitySelection
  // specify the parameters that may be passed as props to the Tirib component
}

const Tirib = ({entity}: TiribProps, { app }: { app: AppHook }) => {
  return (
    <div>
      <Topbar entity={entity} settings={app.settings}/>
      <h1>Tirib</h1>
      <Footer />
    </div>
  )
}

// this component is exported so we can import it somewhere else
// in our case, it'll  be imported inside the file front/src/carbure/index.tsx
export default Tirib
