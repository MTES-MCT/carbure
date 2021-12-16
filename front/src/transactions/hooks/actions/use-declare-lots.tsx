import { Entity } from "carbure/types"
import { prompt } from "common/components/dialog"
import { DeclarationSummaryPrompt } from "../../components/declaration-summary"

export interface LotDeclarator {
  confirmDeclaration: () => Promise<any>
}

export default function useDeclareLots(entity: Entity): LotDeclarator {
  async function confirmDeclaration() {
    if (!entity) return

    await prompt((resolve) => (
      <DeclarationSummaryPrompt entityID={entity.id} onResolve={resolve} />
    ))
  }

  return { confirmDeclaration }
}
