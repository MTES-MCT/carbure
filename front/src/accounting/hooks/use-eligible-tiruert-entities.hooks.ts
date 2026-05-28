import { findEligibleTiruertEntities } from "accounting/components/recipient-form/api"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useMemo } from "react"

export const useEligibleTiruertEntities = (
  selectedEntityId?: string | number
) => {
  const entity = useEntity()
  const { result: entities, loading } = useQuery(findEligibleTiruertEntities, {
    key: `eligible-tiruert-entities-${entity.id}`,
    params: [entity.id, ""],
  })

  const isEntityMatchWithEntities = (selectedEntityId: string | number) =>
    entities?.some((entity) => entity.id === Number(selectedEntityId))

  const selectedEntity = useMemo(
    () =>
      selectedEntityId && entities
        ? entities.find((candidate) => candidate.id === selectedEntityId)
        : undefined,
    [selectedEntityId, entities]
  )

  return { entities, loading, isEntityMatchWithEntities, selectedEntity }
}
