import { Entity } from "common/types"

export interface DashboardDeclaration {
  count: {
    drafts: number
    input: number
    output: number
    corrections: number
  }
  declaration: {
    entity: Entity
    declared: boolean
    checked: boolean
    deadline: string
    period: string
    reminder_count: number
  }
}
