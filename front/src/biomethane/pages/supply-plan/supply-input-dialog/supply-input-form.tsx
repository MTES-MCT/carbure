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

export const SupplyInputForm = () => {
  const { t } = useTranslation()
  const sourceOptions = getSupplyPlanInputSourceOptions()
  const cropTypeOptions = getSupplyPlanInputCropTypeOptions()
  const categoryOptions = getSupplyPlanInputCategoryOptions()
  const materialUnitOptions = getSupplyPlanInputMaterialUnitOptions()
  return (
    <Grid gap="lg" cols={2}>
      <Dialog.Section label="Intrant" gap="lg">
        <RadioGroup
          options={sourceOptions}
          label={t("Provenance")}
          required
          orientation="horizontal"
        />
        <RadioGroup
          options={cropTypeOptions}
          label={t("Type de culture")}
          required
          orientation="horizontal"
        />
        <SelectDsfr
          options={categoryOptions}
          label={t("Catégorie intrants")}
          required
        />
        <SelectDsfr options={categoryOptions} label={t("Intrants")} required />
        <RadioGroup
          options={materialUnitOptions}
          label={t("Unité matière")}
          required
          orientation="horizontal"
        />
        <NumberInput
          label={t("Ratio de matière sèche")}
          min={0}
          max={100}
          required
        />
        <NumberInput
          label={t("Volume (tMB ou tMS en fonction du choix")}
          required
        />
      </Dialog.Section>
      <Dialog.Section label="Réception" gap="lg">
        <AutoCompleteCountries label={t("Pays d'origine")} required />
        <AutoCompleteDepartments label={t("Département d'origine")} required />
        <NumberInput
          label={t("Distance moyenne pondérée d'approvisionnement (Km)")}
        />
        <NumberInput label={t("Distance maximale (Km)")} />
      </Dialog.Section>
    </Grid>
  )
}
