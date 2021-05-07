import { EntitySelection } from "carbure/hooks/use-entity"
import { prompt } from "common/components/dialog"
import { DeclarationSummaryPrompt } from "../../components/declaration-summary"

export interface LotDeclarator {
  confirmDeclaration: () => Promise<any>
}

export default function useDeclareLots(entity: EntitySelection): LotDeclarator {
  async function confirmDeclaration() {
    if (!entity) return

    await prompt((resolve) => (
      <DeclarationSummaryPrompt entityID={entity.id} onResolve={resolve} />
    ))
  }

  return { confirmDeclaration }
}
