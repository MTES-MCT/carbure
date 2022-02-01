import * as adminApi from "./admin"
import * as auditorApi from "./auditor"
import { EntityManager } from "carbure/hooks/entity"

export default function pickApi(entity: EntityManager) {
  if (entity.isAdmin) return adminApi
  else if (entity.isAuditor) return auditorApi
  else throw new Error("Entity is not allowed to do controls")
}
