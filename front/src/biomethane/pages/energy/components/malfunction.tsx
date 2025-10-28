import { ManagedEditableCard } from "common/molecules/editable-card/managed-editable-card"
import { useTranslation } from "react-i18next"
import { MalfunctionTypes } from "../types"
import { useFormContext } from "common/components/form2"
import { useSaveEnergy } from "../energy.hooks"
import { Button } from "common/components/button2"
import { Grid } from "common/components/scaffold"
import { NumberInput, RadioGroup, TextInput } from "common/components/inputs2"
import { getYesNoOptions } from "common/utils/normalizers"
import { useMemo } from "react"
import { DeepPartial } from "common/types"
import { BiomethaneEnergyInputRequest } from "../types"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { EditableCard } from "common/molecules/editable-card"

type MalfunctionForm = DeepPartial<
  Pick<
    BiomethaneEnergyInputRequest,
    | "has_malfunctions"
    | "malfunction_cumulative_duration_days"
    | "malfunction_types"
    | "malfunction_details"
    | "has_injection_difficulties_due_to_network_saturation"
    | "injection_impossibility_hours"
  >
>

const extractValues = (energy?: MalfunctionForm) => {
  return {
    has_malfunctions: energy?.has_malfunctions,
    malfunction_cumulative_duration_days:
      energy?.malfunction_cumulative_duration_days,
    malfunction_types: energy?.malfunction_types,
    malfunction_details: energy?.malfunction_details,
    has_injection_difficulties_due_to_network_saturation:
      energy?.has_injection_difficulties_due_to_network_saturation,
    injection_impossibility_hours: energy?.injection_impossibility_hours,
  }
}

export const Malfunction = () => {
  const { t } = useTranslation()
  const { bind, value } = useFormContext<MalfunctionForm>()
  const saveEnergy = useSaveEnergy()
  const { canEditDeclaration } = useAnnualDeclaration()

  const dysfunctionOptions = useMemo(
    () => [
      { value: MalfunctionTypes.CONCEPTION, label: t("Conception") },
      {
        value: MalfunctionTypes.MAINTENANCE,
        label: t("Entretien/Maintenance"),
      },
      { value: MalfunctionTypes.BIOLOGICAL, label: t("Biologique") },
      { value: MalfunctionTypes.ACCIDENT, label: t("Accident déversement") },
      { value: MalfunctionTypes.PURIFIER, label: t("Épurateur") },
      {
        value: MalfunctionTypes.INJECTION_POST,
        label: t(
          "Poste d'injection (autre que problématiques de saturation des réseaux)"
        ),
      },
      { value: MalfunctionTypes.INPUTS, label: t("Intrants") },
      { value: MalfunctionTypes.OTHER, label: t("Autres (à préciser)") },
    ],
    [t]
  )

  return (
    <ManagedEditableCard
      sectionId="malfunction"
      title={t("Dysfonctionnements")}
      readOnly={!canEditDeclaration}
    >
      {({ isEditing }) => (
        <EditableCard.Form
          onSubmit={() => saveEnergy.execute(extractValues(value))}
        >
          <Grid cols={2} gap="lg">
            <RadioGroup
              readOnly={!isEditing}
              label={t("Y'a t-il eu des dysfonctionnements ?")}
              options={getYesNoOptions()}
              orientation="horizontal"
              required
              {...bind("has_malfunctions")}
            />
            {value.has_malfunctions && (
              <NumberInput
                readOnly={!isEditing}
                label={t("Durée cumulée du dysfonctionnement (en jours)")}
                required
                {...bind("malfunction_cumulative_duration_days")}
              />
            )}
          </Grid>
          {value.has_malfunctions && (
            <>
              <RadioGroup
                readOnly={!isEditing}
                label={t("Types de dysfonctionnement")}
                options={dysfunctionOptions}
                required
                {...bind("malfunction_types")}
              />
              {value.malfunction_types === MalfunctionTypes.OTHER && (
                <TextInput
                  readOnly={!isEditing}
                  label={t("Précisions")}
                  required
                  {...bind("malfunction_details")}
                />
              )}
            </>
          )}
          <RadioGroup
            readOnly={!isEditing}
            label={t(
              "Difficultés pour l'injection dans le réseau de gaz en raison de périodes de saturation des réseaux"
            )}
            options={getYesNoOptions()}
            orientation="horizontal"
            required
            {...bind("has_injection_difficulties_due_to_network_saturation")}
          />
          {value.has_injection_difficulties_due_to_network_saturation && (
            <NumberInput
              readOnly={!isEditing}
              label={t("Nombre d’heures d’impossibilité d’injection (h)")}
              required
              {...bind("injection_impossibility_hours")}
            />
          )}

          {isEditing && (
            <Button
              type="submit"
              iconId="ri-save-line"
              asideX
              loading={saveEnergy.loading}
            >
              {t("Sauvegarder")}
            </Button>
          )}
        </EditableCard.Form>
      )}
    </ManagedEditableCard>
  )
}
