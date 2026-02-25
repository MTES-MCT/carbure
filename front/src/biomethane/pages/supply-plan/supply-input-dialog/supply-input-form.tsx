import { Dialog } from "common/components/dialog2"
import { NumberInput, RadioGroup, TextInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { useTranslation } from "react-i18next"
import {
  getSupplyPlanInputMaterialUnitOptions,
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
          <AutoCompleteFeedstocks
            isMethanogenic
            label={t("Intrants")}
            required
            {...bind("feedstock")}
            readOnly={readOnly}
          />
          {value?.feedstock?.classification?.category ===
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
          {(value?.feedstock?.code === "AUTRES-CULTURES" ||
            value?.feedstock?.code === "AUTRES-CULTURES-CIVE") && (
            <TextInput
              label={t("Précisez la culture")}
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
              label={t("Type de collecte")}
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
                label={t("Unité matière")}
                required={!isBiogazIsdnd}
                orientation="horizontal"
                {...bind("material_unit")}
                readOnly={readOnly}
              />
              {value?.material_unit ===
                BiomethaneSupplyInputMaterialUnit.DRY && (
                <>
                  <NumberInput
                    label={t("Ratio de matière sèche")}
                    min={0}
                    max={100}
                    required={!isBiogazIsdnd}
                    {...bind("dry_matter_ratio_percent")}
                    readOnly={readOnly}
                  />
                  <NumberInput
                    label={t("Tonnage (tMS)")}
                    min={0}
                    required={!isBiogazIsdnd}
                    {...bind("volume")}
                    readOnly={readOnly}
                  />
                </>
              )}
              {value?.material_unit ===
                BiomethaneSupplyInputMaterialUnit.WET && (
                <NumberInput
                  label={t("Tonnage (tMB)")}
                  min={0}
                  required={!isBiogazIsdnd}
                  {...bind("volume")}
                  readOnly={readOnly}
                />
              )}
            </>
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
