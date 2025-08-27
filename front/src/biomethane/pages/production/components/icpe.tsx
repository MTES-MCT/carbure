import { Button } from "common/components/button2"
import { RadioGroup, TextInput } from "common/components/inputs2"
import { EditableCard } from "common/molecules/editable-card"
import { useTranslation } from "react-i18next"
import { useForm } from "common/components/form2"
import { DeepPartial } from "common/types"
import {
  IcpeRegime,
  BiomethaneProductionUnit,
  BiomethaneProductionUnitPatchRequest,
} from "../types"
import { useSaveProductionUnit } from "../production.hooks"

type ICPEForm = DeepPartial<BiomethaneProductionUnitPatchRequest>

export function ICPE({
  productionUnit,
}: {
  productionUnit?: BiomethaneProductionUnit
}) {
  const { t } = useTranslation()

  const { bind, value } = useForm<ICPEForm>({
    icpe_number: productionUnit?.icpe_number,
    icpe_regime: productionUnit?.icpe_regime,
  })

  const { execute: saveProductionUnit, loading } = useSaveProductionUnit()

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
    <EditableCard title={t("ICPE")}>
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={() => saveProductionUnit(value!)}>
          <TextInput
            required
            readOnly={!isEditing}
            label={t("N° ICPE")}
            state="info"
            pattern="\d{10}"
            hintText={t("Code à 10 chiffres")}
            {...bind("icpe_number")}
          />
          <RadioGroup
            required
            readOnly={!isEditing}
            label={t("Régime ICPE")}
            orientation="horizontal"
            options={icpeRegimeOptions}
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
        </EditableCard.Form>
      )}
    </EditableCard>
  )
}
