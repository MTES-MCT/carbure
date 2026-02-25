import { Dialog } from "common/components/dialog2"
import { NumberInput, RadioGroup, TextInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { useTranslation } from "react-i18next"
import {
  getSupplyPlanInputCropTypeOptions,
  getSupplyPlanInputMaterialUnitOptions,
  getSupplyPlanInputSourceOptions,
  getSupplyPlanInputTypeCiveOptions,
  getSupplyPlanInputCollectionTypeOptions,
  SUPPLY_PLAN_INPUT_NAMES_REQUIRING_COLLECTION_TYPE,
} from "../utils"
import { AutoCompleteCountries } from "common/molecules/autocomplete-countries"
import { AutoCompleteDepartments } from "common/molecules/autocomplete-departments"
import { Form, useForm } from "common/components/form2"
import {
  BiomethaneSupplyInput,
  BiomethaneSupplyInputMaterialUnit,
} from "../types"
import { AutoCompleteFeedstocks } from "common/molecules/autocomplete-feedstocks"

type SupplyInputFormValue = Partial<BiomethaneSupplyInput>

export const SupplyInputForm = ({
  supplyInput,
  onSubmit,
  readOnly = false,
}: {
  supplyInput?: BiomethaneSupplyInput
  onSubmit: (value?: BiomethaneSupplyInput) => void
  readOnly?: boolean
}) => {
  const { t } = useTranslation()
  const sourceOptions = getSupplyPlanInputSourceOptions()
  const cropTypeOptions = getSupplyPlanInputCropTypeOptions()
  const materialUnitOptions = getSupplyPlanInputMaterialUnitOptions()
  const typeCiveOptions = getSupplyPlanInputTypeCiveOptions()
  const collectionTypeOptions = getSupplyPlanInputCollectionTypeOptions()

  const form = useForm<SupplyInputFormValue>(supplyInput ?? {})
  const { value, bind } = form
  const isFranceOriginCountry = value.origin_country?.code_pays == "FR"

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
            readOnly={readOnly}
          />
          <RadioGroup
            options={cropTypeOptions}
            label={t("Type de culture")}
            required
            orientation="horizontal"
            {...bind("crop_type")}
            readOnly={readOnly}
          />
          <AutoCompleteFeedstocks
            isMethanogenic
            label={t("Intrants")}
            required
            {...bind("input_name")}
            readOnly={readOnly}
          />
          {value?.input_name?.classification?.category ===
            "Biomasse agricole - Cultures intermédiaires" && (
            <RadioGroup
              options={typeCiveOptions}
              label={t("Type de cive")}
              required
              orientation="horizontal"
              {...bind("type_cive")}
              readOnly={readOnly}
            />
          )}
          {(value?.input_name?.code === "AUTRES_CULTURES" ||
            value?.input_name?.code === "AUTRES_CULTURES_CIVE") && (
            <TextInput
              label={t("Précisez la culture")}
              required
              {...bind("culture_details")}
              readOnly={readOnly}
            />
          )}
          {(
            SUPPLY_PLAN_INPUT_NAMES_REQUIRING_COLLECTION_TYPE as readonly string[]
          ).includes(value?.input_name?.name ?? "") && (
            <RadioGroup
              options={collectionTypeOptions}
              label={t("Type de collecte")}
              required
              orientation="vertical"
              {...bind("collection_type")}
              readOnly={readOnly}
            />
          )}
          {value?.input_name?.classification && (
            <>
              <TextInput
                label={t("Sous-catégorie d'intrants")}
                value={value.input_name.classification.subcategory ?? ""}
                readOnly
              />
              <TextInput
                label={t("Catégorie d'intrants")}
                value={value.input_name.classification.category ?? ""}
                readOnly
              />
              <TextInput
                label={t("Type")}
                value={value.input_name.classification.group ?? ""}
                readOnly
              />
            </>
          )}
          <RadioGroup
            options={materialUnitOptions}
            label={t("Unité matière")}
            required
            orientation="horizontal"
            {...bind("material_unit")}
            readOnly={readOnly}
          />
          {value?.material_unit === BiomethaneSupplyInputMaterialUnit.DRY && (
            <>
              <NumberInput
                label={t("Ratio de matière sèche")}
                min={0}
                max={100}
                required
                {...bind("dry_matter_ratio_percent")}
                readOnly={readOnly}
              />
              <NumberInput
                label={t("Tonnage (tMS)")}
                min={0}
                required
                {...bind("volume")}
                readOnly={readOnly}
              />
            </>
          )}
          {value?.material_unit === BiomethaneSupplyInputMaterialUnit.WET && (
            <NumberInput
              label={t("Tonnage (tMB)")}
              min={0}
              required
              {...bind("volume")}
              readOnly={readOnly}
            />
          )}
        </Dialog.Section>
        <Dialog.Section label="Réception" gap="lg">
          <AutoCompleteCountries
            label={t("Pays d'origine")}
            required
            {...bind("origin_country")}
            readOnly={readOnly}
          />
          {isFranceOriginCountry && (
            <AutoCompleteDepartments
              label={t("Département d'origine")}
              required
              {...bind("origin_department")}
              readOnly={readOnly}
            />
          )}
          <NumberInput
            label={t("Distance moyenne pondérée d'approvisionnement (Km)")}
            min={0}
            {...bind("average_weighted_distance_km")}
            readOnly={readOnly}
            required={isFranceOriginCountry}
          />
          <NumberInput
            label={t("Distance maximale (Km)")}
            min={0}
            {...bind("maximum_distance_km")}
            readOnly={readOnly}
            required={isFranceOriginCountry}
          />
        </Dialog.Section>
      </Grid>
    </Form>
  )
}
