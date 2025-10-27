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
  BiomethaneProductionUnitPatchRequest,
  HygienizationExemptionType,
} from "../types"
import { useSaveProductionUnit } from "../production.hooks"

type SanitaryAgreementForm = DeepPartial<BiomethaneProductionUnitPatchRequest>

export function SanitaryAgreement({
  productionUnit,
}: {
  productionUnit?: BiomethaneProductionUnit
}) {
  const { t } = useTranslation()

  const { bind, value } = useForm<SanitaryAgreementForm>({
    has_sanitary_approval: productionUnit?.has_sanitary_approval,
    sanitary_approval_number: productionUnit?.sanitary_approval_number,
    has_hygienization_exemption: productionUnit?.has_hygienization_exemption,
    hygienization_exemption_type: productionUnit?.hygienization_exemption_type,
  })

  const { execute: saveProductionUnit, loading } =
    useSaveProductionUnit(productionUnit)

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
        <EditableCard.Form onSubmit={() => saveProductionUnit(value!)}>
          <Grid cols={2} gap="lg">
            <RadioGroup
              required
              readOnly={!isEditing}
              label={t("Votre site dispose-t-il d'un agrément sanitaire ?")}
              options={getYesNoOptions()}
              orientation="horizontal"
              {...bind("has_sanitary_approval")}
            />
            {value.has_sanitary_approval && (
              <TextInput
                required
                readOnly={!isEditing}
                label={t("N° Agrément sanitaire")}
                placeholder="FR XX-XX-XXX"
                {...bind("sanitary_approval_number")}
              />
            )}
          </Grid>
          <Grid cols={2} gap="lg">
            <RadioGroup
              required
              readOnly={!isEditing}
              label={t("Disposez vous d'une dérogation à l'hygiénisation?")}
              options={getYesNoOptions()}
              orientation="horizontal"
              {...bind("has_hygienization_exemption")}
            />
            {value.has_hygienization_exemption && (
              <RadioGroup
                required
                readOnly={!isEditing}
                label={t("Si oui, dérogation à l'hygiénisation :")}
                options={hygienizationExemptionOptions}
                orientation="horizontal"
                {...bind("hygienization_exemption_type")}
              />
            )}
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
