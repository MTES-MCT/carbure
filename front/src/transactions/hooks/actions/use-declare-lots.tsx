import { EntitySelection } from "carbure/hooks/use-entity"
import { prompt } from "common/components/dialog"
import { SummaryPromptFactory } from "../../components/declaration-summary"

export interface LotDeclarator {
  confirmDeclaration: () => Promise<any>
}

export default function useDeclareLots(entity: EntitySelection): LotDeclarator {
  async function confirmDeclaration() {
    if (!entity) return

    await prompt(
      "Déclaration de durabilité",
      "",
      SummaryPromptFactory(entity.id)
    )
  }

  return { confirmDeclaration }
}
