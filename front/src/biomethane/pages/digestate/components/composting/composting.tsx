import { Button } from "common/components/button2"
import {
  TextInput,
  NumberInput,
  CheckboxGroup,
} from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { EditableCard } from "common/molecules/editable-card"
import { useTranslation } from "react-i18next"
import { useForm } from "common/components/form2"
import { DeepPartial } from "common/types"
import {
  BiomethaneDigestate,
  BiomethaneDigestateInputRequest,
  BiomethaneDigestateCompostingLocation,
} from "../../types"
import { AutoCompleteDepartments } from "common/molecules/autocomplete-departments"
import { useSaveDigestate } from "../../digestate.hooks"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration.provider"

type CompostingForm = DeepPartial<
  Pick<
    BiomethaneDigestateInputRequest,
    | "external_platform_name"
    | "external_platform_department"
    | "external_platform_municipality"
    | "on_site_composted_digestate_volume"
    | "external_platform_digestate_volume"
  >
> &
  Pick<BiomethaneDigestateInputRequest, "composting_locations">

export function Composting({ digestate }: { digestate?: BiomethaneDigestate }) {
  const { t } = useTranslation()
  const { bind, value } = useForm<CompostingForm>(
    digestate
      ? {
          external_platform_name: digestate.external_platform_name,
          external_platform_department: digestate.external_platform_department,
          external_platform_municipality:
            digestate.external_platform_municipality,
          on_site_composted_digestate_volume:
            digestate.on_site_composted_digestate_volume,
          external_platform_digestate_volume:
            digestate.external_platform_digestate_volume,
          composting_locations: digestate.composting_locations,
        }
      : {}
  )
  const saveDigestate = useSaveDigestate()
  const { canEditDeclaration } = useAnnualDeclaration()

  const handleSave = async () => saveDigestate.execute(value)

  const compostingOptions = [
    {
      value: BiomethaneDigestateCompostingLocation.ON_SITE,
      label: t("Sur site"),
    },
    {
      value: BiomethaneDigestateCompostingLocation.EXTERNAL_PLATFORM,
      label: t("Plateforme externe"),
    },
  ]

  const isExternalPlatformSelected = value.composting_locations?.includes(
    BiomethaneDigestateCompostingLocation.EXTERNAL_PLATFORM
  )

  const isOnSiteSelected = value.composting_locations?.includes(
    BiomethaneDigestateCompostingLocation.ON_SITE
  )

  return (
    <EditableCard
      title={t("Lieu du compostage")}
      readOnly={!canEditDeclaration}
    >
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={handleSave}>
          <CheckboxGroup
            options={compostingOptions}
            {...bind("composting_locations")}
            readOnly={!isEditing}
            label={t("Lieu du compostage")}
            orientation="horizontal"
          />
          {isExternalPlatformSelected && (
            <Grid cols={2} gap="lg">
              <TextInput
                readOnly={!isEditing}
                label={t("Nom de la plateforme externe")}
                {...bind("external_platform_name")}
                required
              />
              <NumberInput
                readOnly={!isEditing}
                label={t(
                  "Volume de digestat composté sur la plateforme externe (t)"
                )}
                type="number"
                {...bind("external_platform_digestate_volume")}
                required
              />

              <AutoCompleteDepartments
                readOnly={!isEditing}
                label={t("Département de la plateforme externe")}
                {...bind("external_platform_department")}
                required
              />
              <TextInput
                readOnly={!isEditing}
                label={t("Commune de la plateforme externe")}
                {...bind("external_platform_municipality")}
                required
              />
            </Grid>
          )}
          {isOnSiteSelected && (
            <NumberInput
              readOnly={!isEditing}
              label={t("Volume de digestat composté sur site (t)")}
              {...bind("on_site_composted_digestate_volume")}
              required
            />
          )}
          {isEditing && (
            <Button
              type="submit"
              iconId="ri-save-line"
              asideX
              loading={saveDigestate.loading}
            >
              {t("Sauvegarder")}
            </Button>
          )}
        </EditableCard.Form>
      )}
    </EditableCard>
  )
}
