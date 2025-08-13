import { Button } from "common/components/button2"
import { RadioGroup, TextInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { EditableCard } from "common/molecules/editable-card"
import { getYesNoOptions } from "common/utils/normalizers"
import { useTranslation } from "react-i18next"
import { useForm } from "common/components/form2"
import { DeepPartial } from "common/types"
import {
  BiomethaneProductionUnit,
  BiomethaneProductionUnitAddRequest,
  HygienizationExemptionType,
} from "../../types"
import { useMutateProductionUnit } from "../../production.hooks"

type SanitaryAgreementForm = DeepPartial<BiomethaneProductionUnitAddRequest>

export function SanitaryAgreement({
  productionUnit,
}: {
  productionUnit?: BiomethaneProductionUnit
}) {
  const { t } = useTranslation()
  const { bind, value } = useForm<SanitaryAgreementForm>(productionUnit ?? {})
  const { execute: updateProductionUnit, loading } = useMutateProductionUnit(
    productionUnit !== undefined
  )

  const hygienizationExemptionOptions = [
    {
      label: t("Totale"),
      value: HygienizationExemptionType.TOTAL,
    },
    {
      label: t("Partielle"),
      value: HygienizationExemptionType.PARTIAL,
    },
  ]

  return (
    <EditableCard title={t("Agrément sanitaire")}>
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={() => updateProductionUnit(value!)}>
          <Grid cols={2} gap="lg">
            <RadioGroup
              readOnly={!isEditing}
              label={t("Votre site dispose-t-il d'un agrément sanitaire ?")}
              options={getYesNoOptions()}
              orientation="horizontal"
              {...bind("has_sanitary_approval")}
            />
            <TextInput
              readOnly={!isEditing}
              label={t("N° Agrément sanitaire")}
              placeholder="FR XX-XX-XXX"
              {...bind("sanitary_approval_number")}
            />
            <RadioGroup
              readOnly={!isEditing}
              label={t("Disposez vous d'une dérogation à l'hygiénisation?")}
              options={getYesNoOptions()}
              orientation="horizontal"
              {...bind("has_hygienization_exemption")}
            />
            <RadioGroup
              readOnly={!isEditing}
              label={t("Si oui, dérogation à l'hygiénisation :")}
              options={hygienizationExemptionOptions}
              orientation="horizontal"
              {...bind("hygienization_exemption_type")}
            />
          </Grid>
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
