import { patchAnnualDeclaration } from "biomethane/api"
import {
  useAnnualDeclaration,
  useAnnualDeclarationYear,
} from "biomethane/providers/annual-declaration"
import { Button } from "common/components/button2"
import { useMutation } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useSelectedEntity } from "common/providers/selected-entity-provider"
import { useTranslation } from "react-i18next"

export const ToggleDeclarationButton = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { selectedEntityId } = useSelectedEntity()
  const selectedYear = useAnnualDeclarationYear()
  const { annualDeclaration, annualDeclarationKey } = useAnnualDeclaration()

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
  return (
    <Button
      onClick={() => mutation.execute(annualDeclaration?.is_open ?? false)}
      loading={mutation.loading}
      priority="secondary"
      asideX
    >
      {annualDeclaration?.is_open
        ? t("Fermer la déclaration")
        : t("Ouvrir la déclaration")}
    </Button>
  )
}
