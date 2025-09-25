import { Dialog } from "common/components/dialog2"
import { NumberInput, RadioGroup } from "common/components/inputs2"
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
import { useForm } from "common/components/form2"
import { BiomethaneSupplyInput, BiomethaneSupplyInputForm } from "../types"

type SupplyInputFormValue = Partial<BiomethaneSupplyInputForm>

export const SupplyInputForm = ({
  supplyInput,
}: {
  supplyInput?: BiomethaneSupplyInput
}) => {
  const { t } = useTranslation()
  const sourceOptions = getSupplyPlanInputSourceOptions()
  const cropTypeOptions = getSupplyPlanInputCropTypeOptions()
  const categoryOptions = getSupplyPlanInputCategoryOptions()
  const materialUnitOptions = getSupplyPlanInputMaterialUnitOptions()

  const { bind } = useForm<SupplyInputFormValue>(supplyInput ?? {})

  return (
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
        <SelectDsfr options={categoryOptions} label={t("Intrants")} required />
        <RadioGroup
          options={materialUnitOptions}
          label={t("Unité matière")}
          required
          orientation="horizontal"
          {...bind("material_unit")}
        />
        <NumberInput
          label={t("Ratio de matière sèche")}
          min={0}
          max={100}
          required
          {...bind("dry_matter_ratio_percent")}
        />
        <NumberInput
          label={t("Volume (tMB ou tMS en fonction du choix")}
          required
          {...bind("volume")}
        />
      </Dialog.Section>
      <Dialog.Section label="Réception" gap="lg">
        <AutoCompleteCountries label={t("Pays d'origine")} required />
        <AutoCompleteDepartments label={t("Département d'origine")} required />
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
  )
}
