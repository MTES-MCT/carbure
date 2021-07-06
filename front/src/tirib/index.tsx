import { Entity, EntityType } from "common/types"

// check if a given entity can have access to the tirib page
export function hasTirib(entity: Entity | null): boolean {
  if (entity === null) return false
  else if (entity.entity_type === EntityType.Operator) return true
  else if (entity.has_mac) return true
  else return false
}

type TiribProps = {
  // specify the parameters that may be passed as props to the Tirib component
}

const Tirib = (props: TiribProps) => {
  return (
    <div>
      <h1>Tirib</h1>
    </div>
  )
}

// this component is exported so we can import it somewhere else
// in our case, it'll  be imported inside the file front/src/carbure/index.tsx
export default Tirib
