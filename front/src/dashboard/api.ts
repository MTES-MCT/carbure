import api from "common/services/api"
import { Entity } from "common/types"
import {
  DeclarationsByEntityType,
  groupDeclarationsByEntities,
} from "./helpers"

export function getDeclarations(
  year: number,
  month: number
): Promise<[Entity[], string[], DeclarationsByEntityType]> {
  return api
    .get("/admin/dashboard/declarations", { year, month })
    .then(groupDeclarationsByEntities)
}

export function checkDeclaration(id: number): Promise<any> {
  return api.post("/admin/dashboard/declaration/check", { id })
}

export function uncheckDeclaration(id: number): Promise<any> {
  return api.post("/admin/dashboard/declaration/uncheck", { id })
}

export function sendDeclarationReminder(
  entity_id: number,
  year: number,
  month: number
): Promise<any> {
  return api.post("/admin/dashboard/declaration/send-reminder", {
    entity_id,
    year,
    month,
  })
}
