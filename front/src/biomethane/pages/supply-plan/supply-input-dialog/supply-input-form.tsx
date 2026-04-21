import { Dialog } from "common/components/dialog2"
import { NumberInput, RadioGroup, TextInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { useTranslation } from "react-i18next"
import {
  getSupplyPlanInputMaterialUnitOptions,
  getSupplyPlanInputTypeCiveOptions,
  getSupplyPlanInputCollectionTypeOptions,
  getSupplyPlanInputSourceOptions,
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
import { useBiomethaneBackendInputLabel } from "biomethane/hooks/use-biomethane-backend-input-label"

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
  const tBiomethaneInput = useBiomethaneBackendInputLabel()
  const sourceOptions = getSupplyPlanInputSourceOptions()
  const materialUnitOptions = getSupplyPlanInputMaterialUnitOptions()
  const typeCiveOptions = getSupplyPlanInputTypeCiveOptions()
  const collectionTypeOptions = getSupplyPlanInputCollectionTypeOptions()

  const form = useForm<SupplyInputFormValue>(supplyInput ?? {})
  const { value, bind } = form
  const isFranceOriginCountry = value.origin_country?.code_pays == "FR"
  const isBiogazIsdnd = value?.feedstock?.code === "BIOGAZ-CAPTE-DUNE-ISDND"

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
            label={tBiomethaneInput("supply_input.source")}
            orientation="horizontal"
            {...bind("source")}
            readOnly={readOnly}
          />
          <AutoCompleteFeedstocks
            label={tBiomethaneInput("supply_input.feedstock")}
            required
            {...bind("feedstock")}
            readOnly={readOnly}
          />
          {value?.feedstock?.classification?.category ===
            "Biomasse agricole - Cultures intermédiaires" && (
            <RadioGroup
              options={typeCiveOptions}
              label={tBiomethaneInput("supply_input.type_cive")}
              required
              orientation="horizontal"
              {...bind("type_cive")}
              readOnly={readOnly}
            />
          )}
          {(value?.feedstock?.code === "AUTRES-CULTURES" ||
            value?.feedstock?.code === "AUTRES-CULTURES-CIVE") && (
            <TextInput
              label={tBiomethaneInput("supply_input.culture_details")}
              required
              {...bind("culture_details")}
              readOnly={readOnly}
            />
          )}
          {SUPPLY_PLAN_INPUT_NAMES_REQUIRING_COLLECTION_TYPE.includes(
            value?.feedstock?.code ?? ""
          ) && (
            <RadioGroup
              options={collectionTypeOptions}
              label={tBiomethaneInput("supply_input.collection_type")}
              required
              orientation="vertical"
              {...bind("collection_type")}
              readOnly={readOnly}
            />
          )}
          {value?.feedstock?.classification && (
            <>
              <TextInput
                label={t("Sous-catégorie d'intrants")}
                value={value.feedstock.classification.subcategory ?? ""}
                readOnly
              />
              <TextInput
                label={t("Catégorie d'intrants")}
                value={value.feedstock.classification.category ?? ""}
                readOnly
              />
              <TextInput
                label={t("Type")}
                value={value.feedstock.classification.group ?? ""}
                readOnly
              />
            </>
          )}
          {!isBiogazIsdnd && (
            <>
              <RadioGroup
                options={materialUnitOptions}
                label={tBiomethaneInput("supply_input.material_unit")}
                required={!isBiogazIsdnd}
                orientation="horizontal"
                {...bind("material_unit")}
                readOnly={readOnly}
              />
              {value?.material_unit ===
                BiomethaneSupplyInputMaterialUnit.DRY && (
                <>
                  <NumberInput
                    label={tBiomethaneInput(
                      "supply_input.dry_matter_ratio_percent"
                    )}
                    min={0}
                    max={100}
                    required={!isBiogazIsdnd}
                    {...bind("dry_matter_ratio_percent")}
                    readOnly={readOnly}
                    step={0.01}
                  />
                  <NumberInput
                    label={tBiomethaneInput("supply_input.volume")}
                    min={0}
                    required={!isBiogazIsdnd}
                    {...bind("volume")}
                    readOnly={readOnly}
                    step={0.01}
                  />
                </>
              )}
              {value?.material_unit ===
                BiomethaneSupplyInputMaterialUnit.WET && (
                <NumberInput
                  label={tBiomethaneInput("supply_input.volume")}
                  min={0}
                  required={!isBiogazIsdnd}
                  {...bind("volume")}
                  readOnly={readOnly}
                  step={0.01}
                />
              )}
            </>
          )}
        </Dialog.Section>
        <Dialog.Section label="Réception" gap="lg">
          <AutoCompleteCountries
            label={tBiomethaneInput("supply_input.origin_country")}
            required
            {...bind("origin_country")}
            readOnly={readOnly}
          />
          {isFranceOriginCountry && (
            <AutoCompleteDepartments
              label={tBiomethaneInput("supply_input.origin_department")}
              required
              {...bind("origin_department")}
              readOnly={readOnly}
            />
          )}
          <NumberInput
            label={tBiomethaneInput(
              "supply_input.average_weighted_distance_km"
            )}
            min={0}
            {...bind("average_weighted_distance_km")}
            readOnly={readOnly}
            required={isFranceOriginCountry}
            max={value?.maximum_distance_km ?? undefined}
            step={0.01}
          />
          <NumberInput
            label={tBiomethaneInput("supply_input.maximum_distance_km")}
            min={0}
            {...bind("maximum_distance_km")}
            readOnly={readOnly}
            required={isFranceOriginCountry}
            step={0.01}
          />
        </Dialog.Section>
      </Grid>
    </Form>
  )
}
