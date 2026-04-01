import { Button } from "common/components/button2"
import { RadioGroup, TextInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { useTranslation } from "react-i18next"
import { useFormContext } from "common/components/form2"
import {
  BiomethaneProductionUnit,
  ProductionUnitForm,
  UnitType,
} from "../types"
import { useSaveProductionUnit } from "../production.hooks"
import { SiretPicker } from "common/molecules/siret-picker"
import { AutoCompleteDepartments } from "common/molecules/autocomplete-departments"
import { useAllowedToEdit } from "biomethane/hooks/use-allowed-to-edit"
import { ManagedEditableCard } from "common/molecules/editable-card/managed-editable-card"

type GeneralInfoForm = Pick<
  ProductionUnitForm,
  | "name"
  | "site_siret"
  | "unit_type"
  | "address"
  | "postal_code"
  | "city"
  | "department"
  | "insee_code"
>

const GENERAL_INFO_SECTION_ID = "general-info"

const extractValues = (form?: GeneralInfoForm) => ({
  name: form?.name,
  site_siret: form?.site_siret,
  unit_type: form?.unit_type,
  address: form?.address,
  postal_code: form?.postal_code,
  city: form?.city,
  department: form?.department,
  insee_code: form?.insee_code,
})

export function GeneralInfo({
  productionUnit,
}: {
  productionUnit?: BiomethaneProductionUnit
}) {
  const { t } = useTranslation()
  const allowedToEdit = useAllowedToEdit()

  const { bind, value, setField } = useFormContext<GeneralInfoForm>()
  const { execute: saveProductionUnit, loading } =
    useSaveProductionUnit(productionUnit)

  const unitTypeOptions = [
    {
      label: t("Agricole autonome"),
      value: UnitType.AGRICULTURAL_AUTONOMOUS,
    },
    {
      label: t("Agricole territorial"),
      value: UnitType.AGRICULTURAL_TERRITORIAL,
    },
    {
      label: t("Industriel territorial"),
      value: UnitType.INDUSTRIAL_TERRITORIAL,
    },
    {
      label: t("Déchets ménagers et biodéchets"),
      value: UnitType.HOUSEHOLD_WASTE_BIOWASTE,
    },
    {
      label: t("STEP"),
      value: UnitType.STEP,
    },
    {
      label: t("ISDND"),
      value: UnitType.ISDND,
    },
  ]

  const handleSubmit = () => {
    saveProductionUnit(extractValues(value))
  }

  return (
    <ManagedEditableCard
      sectionId={GENERAL_INFO_SECTION_ID}
      title={t("Informations générales du site de production")}
      readOnly={!allowedToEdit}
    >
      {({ isEditing }) => (
        <ManagedEditableCard.Form onSubmit={handleSubmit}>
          <Grid cols={2} gap="lg">
            <TextInput
              readOnly={!isEditing}
              label={t("Nom de l'unité")}
              required
              {...bind("name")}
            />
            <SiretPicker
              label={t("SIRET")}
              required
              onSelect={(company) => {
                if (company) {
                  setField("address", company?.registered_address)
                  setField("postal_code", company?.registered_zipcode)
                  setField("city", company?.registered_city)
                  setField("department", company?.department_code)
                  setField("insee_code", company?.insee_code)
                }
              }}
              readOnly={!isEditing}
              {...bind("site_siret")}
            />
          </Grid>
          <TextInput
            readOnly={!isEditing}
            label={t("Adresse de la société (Numéro et rue)")}
            required
            {...bind("address")}
          />
          <Grid cols={2} gap="lg">
            <AutoCompleteDepartments
              readOnly={!isEditing}
              label={t("Département")}
              required
              {...bind("department")}
              onChange={(value) => {
                setField("department", value ?? undefined)
              }}
            />
            <TextInput
              readOnly={!isEditing}
              label={t("Code postal")}
              required
              {...bind("postal_code")}
            />
            <TextInput
              readOnly={!isEditing}
              label={t("Commune")}
              required
              {...bind("city")}
            />
            <TextInput
              readOnly={!isEditing}
              label={t("Code INSEE")}
              required
              {...bind("insee_code")}
            />
          </Grid>
          <RadioGroup
            readOnly={!isEditing}
            label={t("Type d'installation")}
            options={unitTypeOptions}
            required
            {...bind("unit_type")}
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
