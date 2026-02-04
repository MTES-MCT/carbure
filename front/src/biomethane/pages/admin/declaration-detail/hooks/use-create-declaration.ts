import { useMutation } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useSelectedEntity } from "common/providers/selected-entity-provider"
import {
  useAnnualDeclaration,
  useAnnualDeclarationYear,
} from "biomethane/providers/annual-declaration"
import { createDeclaration } from "biomethane/pages/admin/api"

export const useCreateDeclaration = () => {
  const entity = useEntity()
  const { selectedEntityId } = useSelectedEntity()
  const year = useAnnualDeclarationYear()
  const { annualDeclarationKey } = useAnnualDeclaration()

  const mutation = useMutation(
    () => createDeclaration(year!, entity.id, selectedEntityId),
    {
      invalidates: [annualDeclarationKey],
    }
  )

  return mutation
}
