import { ExportButton } from "common/components/export"
import { downloadSupplyPlan } from "../api"
import { useSelectedEntity } from "common/providers/selected-entity-provider"
import { BiomethaneSupplyInputQuery } from "../types"

export const DownloadSupplyPlan = ({
  query,
}: {
  query: BiomethaneSupplyInputQuery
}) => {
  const { selectedEntityId } = useSelectedEntity()
  return (
    <ExportButton
      query={query}
      download={(_query) => downloadSupplyPlan(_query, selectedEntityId)}
    />
  )
}
