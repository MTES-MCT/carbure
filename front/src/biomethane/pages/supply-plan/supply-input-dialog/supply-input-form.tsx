import { Dialog } from "common/components/dialog2"
import { NumberInput, RadioGroup, TextInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { useTranslation } from "react-i18next"
import {
  getSupplyPlanInputCategoryOptions,
  getSupplyPlanInputCropTypeOptions,
  getSupplyPlanInputMaterialUnitOptions,
  getSupplyPlanInputSourceOptions,
} from "../utils"
import { SelectDsfr } from "common/components/selects2"
import { AutoCompleteCountries } from "common/molecules/autocomplete-countries"
import { AutoCompleteDepartments } from "common/molecules/autocomplete-departments"
import { Form, useForm } from "common/components/form2"
import {
  BiomethaneSupplyInput,
  BiomethaneSupplyInputMaterialUnit,
} from "../types"

type SupplyInputFormValue = Partial<BiomethaneSupplyInput>

export const SupplyInputForm = ({
  supplyInput,
  onSubmit,
}: {
  supplyInput?: BiomethaneSupplyInput
  onSubmit: (value?: BiomethaneSupplyInput) => void
}) => {
  const { t } = useTranslation()
  const sourceOptions = getSupplyPlanInputSourceOptions()
  const cropTypeOptions = getSupplyPlanInputCropTypeOptions()
  const categoryOptions = getSupplyPlanInputCategoryOptions()
  const materialUnitOptions = getSupplyPlanInputMaterialUnitOptions()

  const form = useForm<SupplyInputFormValue>(supplyInput ?? {})
  const { value, bind } = form

  return (
    <Form
      id="supply-input-form"
      form={form}
      onSubmit={(value) => onSubmit(value as BiomethaneSupplyInput)}
    >
      <Grid gap="lg" cols={2}>
        <Dialog.Section label="Intrant" gap="lg">
          <RadioGroup
            options={sourceOptions}
            label={t("Provenance")}
            required
            orientation="horizontal"
            {...bind("source")}
          />
          <RadioGroup
            options={cropTypeOptions}
            label={t("Type de culture")}
            required
            orientation="horizontal"
            {...bind("crop_type")}
          />
          <SelectDsfr
            options={categoryOptions}
            label={t("Catégorie intrants")}
            required
            {...bind("input_category")}
          />
          <TextInput
            label={t("Nom des intrants")} //
            required
            {...bind("input_type")}
          />
          <RadioGroup
            options={materialUnitOptions}
            label={t("Unité matière")}
            required
            orientation="horizontal"
            {...bind("material_unit")}
          />
          {value?.material_unit === BiomethaneSupplyInputMaterialUnit.DRY && (
            <>
              <NumberInput
                label={t("Ratio de matière sèche (%)")}
                min={0}
                max={100}
                required
                {...bind("dry_matter_ratio_percent")}
              />
              <NumberInput
                label={t("Tonnage (tMS)")}
                required
                {...bind("volume")}
              />
            </>
          )}
          {value?.material_unit === BiomethaneSupplyInputMaterialUnit.WET && (
            <NumberInput
              label={t("Tonnage (tMB)")}
              required
              {...bind("volume")}
            />
          )}
        </Dialog.Section>
        <Dialog.Section label="Réception" gap="lg">
          <AutoCompleteCountries
            label={t("Pays d'origine")}
            required
            {...bind("origin_country")}
          />
          {value.origin_country?.code_pays == "FR" && (
            <AutoCompleteDepartments
              label={t("Département d'origine")}
              required
              {...bind("origin_department")}
            />
          )}
          <NumberInput
            label={t("Distance moyenne pondérée d'approvisionnement (Km)")}
            {...bind("average_weighted_distance_km")}
          />
          <NumberInput
            label={t("Distance maximale (Km)")}
            {...bind("maximum_distance_km")}
          />
        </Dialog.Section>
      </Grid>
    </Form>
  )
}
