import { EntitySelection } from "carbure/hooks/use-entity"
import { prompt } from "common/components/dialog"
import { SummaryPrompt } from "../../components/declaration-summary"

export interface LotDeclarator {
  confirmDeclaration: () => Promise<any>
}

export default function useDeclareLots(entity: EntitySelection): LotDeclarator {
  async function confirmDeclaration() {
    if (!entity) return

    await prompt((resolve) => (
      <SummaryPrompt entityID={entity.id} onResolve={resolve} />
    ))
  }

  return { confirmDeclaration }
}
