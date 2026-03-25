import { Button } from "common/components/button2"
import { RadioGroup, TextInput } from "common/components/inputs2"
import { useTranslation } from "react-i18next"
import { useFormContext } from "common/components/form2"
import {
  IcpeRegime,
  BiomethaneProductionUnit,
  ProductionUnitForm,
} from "../types"
import { useSaveProductionUnit } from "../production.hooks"
import { useAllowedToEdit } from "biomethane/hooks/use-allowed-to-edit"
import { IcpeNumberHelper } from "./icpe-number-helper"
import { ManagedEditableCard } from "common/molecules/editable-card/managed-editable-card"

type ICPEForm = Pick<ProductionUnitForm, "icpe_number" | "icpe_regime">

const extractValues = (form?: ICPEForm) => ({
  icpe_number: form?.icpe_number,
  icpe_regime: form?.icpe_regime,
})

export function ICPE({
  productionUnit,
}: {
  productionUnit?: BiomethaneProductionUnit
}) {
  const { t } = useTranslation()
  const allowedToEdit = useAllowedToEdit()

  const { bind, value } = useFormContext<ICPEForm>()
  const { execute: saveProductionUnit, loading } =
    useSaveProductionUnit(productionUnit)

  const icpeRegimeOptions = [
    {
      value: IcpeRegime.AUTHORIZATION,
      label: t("Autorisation"),
    },
    {
      value: IcpeRegime.REGISTRATION,
      label: t("Enregistrement"),
    },
    {
      value: IcpeRegime.DECLARATION_PERIODIC_CONTROLS,
      label: t("Déclaration (avec contrôles périodiques)"),
    },
  ]

  return (
    <ManagedEditableCard
      sectionId="icpe"
      title={t("ICPE")}
      readOnly={!allowedToEdit}
    >
      {({ isEditing }) => (
        <ManagedEditableCard.Form
          onSubmit={() => saveProductionUnit(extractValues(value))}
        >
          <TextInput
            required
            readOnly={!isEditing}
            label={t("N° ICPE")}
            state="info"
            pattern="\d{10}"
            hintText={<IcpeNumberHelper />}
            {...bind("icpe_number")}
          />
          <RadioGroup
            required
            readOnly={!isEditing}
            label={t("Régime ICPE")}
            orientation="horizontal"
            options={icpeRegimeOptions}
            hintText={t(
              "Précisez le régime ICPE de l'installation de méthanisation associée à la rubrique 2781 ou 3532"
            )}
            {...bind("icpe_regime")}
          />
          {isEditing && (
            <Button
              type="submit"
              iconId="ri-save-line"
              asideX
              loading={loading}
            >
              {t("Sauvegarder")}
            </Button>
          )}
        </ManagedEditableCard.Form>
      )}
    </ManagedEditableCard>
  )
}
