import { patchAnnualDeclaration } from "biomethane/api"
import {
  useAnnualDeclaration,
  useAnnualDeclarationYear,
} from "biomethane/providers/annual-declaration"
import { useMutation } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useSelectedEntity } from "common/providers/selected-entity-provider"

export const useToggleDeclaration = () => {
  const entity = useEntity()
  const { selectedEntityId } = useSelectedEntity()
  const selectedYear = useAnnualDeclarationYear()
  const { annualDeclarationKey } = useAnnualDeclaration()

  const mutation = useMutation(
    (is_open: boolean) =>
      patchAnnualDeclaration(
        entity.id,
        selectedYear!,
        { is_open: !is_open },
        selectedEntityId
      ),
    {
      invalidates: [annualDeclarationKey],
    }
  )

  return mutation
}
