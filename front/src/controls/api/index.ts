import * as admin from "./admin"
import * as auditor from "./auditor"
import { EntityManager } from "carbure/hooks/entity"

export default function pickApi(entity: EntityManager) {
  return entity.isAdmin ? admin : auditor
}
