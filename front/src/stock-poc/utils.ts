import { EntityPreview } from "common/types"
import { Action } from "./types"
import { ActionFormValue } from "./components/action-form"

export type ActionNode = Action & { children: ActionNode[] }

export function buildActionForest(actions: Action[]): ActionNode[] {
  const byId = new Map<number, ActionNode>(
    actions.map((action) => [action.id, { ...action, children: [] }])
  )
  const roots: ActionNode[] = []

  for (const node of byId.values()) {
    if (node.parent && byId.has(node.parent)) {
      byId.get(node.parent)!.children.push(node)
    } else {
      roots.push(node)
    }
  }

  const sortById = (nodes: ActionNode[]) => {
    nodes.sort((a, b) => a.id - b.id)
    nodes.forEach((node) => sortById(node.children))
  }

  sortById(roots)
  return roots
}

export function actionToFormValue(action: Action): ActionFormValue {
  return {
    type: action.type,
    status: action.status ?? undefined,
    quantity: Number(action.quantity),
    parent: action.parent ?? undefined,
    owner: {
      id: action.owner,
      name: action.owner_name,
    } as EntityPreview,
  }
}
