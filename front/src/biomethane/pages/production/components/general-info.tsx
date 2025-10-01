import { Button } from "common/components/button2"
import { RadioGroup, TextInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { EditableCard } from "common/molecules/editable-card"
import { useTranslation } from "react-i18next"
import { useForm } from "common/components/form2"
import { DeepPartial } from "common/types"
import {
  BiomethaneProductionUnit,
  BiomethaneProductionUnitPatchRequest,
  UnitType,
} from "../types"
import { useSaveProductionUnit } from "../production.hooks"
import { SiretPicker } from "common/molecules/siret-picker"
import { AutoCompleteDepartments } from "common/molecules/autocomplete-departments"

type GeneralInfoForm = DeepPartial<
  Pick<
    BiomethaneProductionUnitPatchRequest,
    | "unit_name"
    | "siret_number"
    | "unit_type"
    | "company_address"
    | "postal_code"
    | "city"
    | "department"
  >
>

export function GeneralInfo({
  productionUnit,
}: {
  productionUnit?: BiomethaneProductionUnit
}) {
  const { t } = useTranslation()

  const { bind, value, setField } = useForm<GeneralInfoForm>({
    unit_name: productionUnit?.unit_name,
    siret_number: productionUnit?.siret_number,
    unit_type: productionUnit?.unit_type,
    company_address: productionUnit?.company_address,
    postal_code: productionUnit?.postal_code,
    city: productionUnit?.city,
    department: productionUnit?.department,
  })

  const { execute: saveProductionUnit, loading } = useSaveProductionUnit()

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
      label: t("ISDND"),
      value: UnitType.ISDND,
    },
  ]

  return (
    <EditableCard title={t("Informations générales du site de production")}>
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={() => saveProductionUnit(value!)}>
          <Grid cols={2} gap="lg">
            <TextInput
              readOnly={!isEditing}
              label={t("Nom de l'unité")}
              required
              {...bind("unit_name")}
            />
            <SiretPicker
              label={t("SIRET")}
              required
              onSelect={(company) => {
                if (company) {
                  setField("company_address", company?.registered_address)
                  setField("postal_code", company?.registered_zipcode)
                  setField("city", company?.registered_city)
                  setField("department", company?.department_code)
                }
              }}
              readOnly={!isEditing}
              {...bind("siret_number")}
            />
          </Grid>
          <TextInput
            readOnly={!isEditing}
            label={t("Adresse de la société (Numéro et rue)")}
            required
            {...bind("company_address")}
          />
          <Grid cols={2} gap="lg">
            <AutoCompleteDepartments
              readOnly={!isEditing}
              label={t("Département")}
              required
              {...bind("department")}
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
        </EditableCard.Form>
      )}
    </EditableCard>
  )
}
