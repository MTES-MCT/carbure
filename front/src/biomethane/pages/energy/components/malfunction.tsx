import { EditableCard } from "common/molecules/editable-card"
import { useTranslation } from "react-i18next"
import { BiomethaneEnergy } from "../types"
import { useForm } from "common/components/form2"
import { useEnergyContext } from "../energy.hooks"
import { Button } from "common/components/button2"
import { Grid } from "common/components/scaffold"
import { NumberInput, RadioGroup, TextInput } from "common/components/inputs2"
import { getYesNoOptions } from "common/utils/normalizers"
import { useMemo } from "react"

type MalfunctionForm = {}

export const Malfunction = ({ energy }: { energy?: BiomethaneEnergy }) => {
  const { t } = useTranslation()
  const { bind, value } = useForm<MalfunctionForm>(energy ?? {})
  const { saveEnergy, isInDeclarationPeriod } = useEnergyContext()

  const dysfunctionOptions = useMemo(
    () => [
      { value: "conception", label: t("Conception") },
      { value: "maintenance", label: t("Entretien/Maintenance") },
      { value: "biological", label: t("Biologique") },
      { value: "equipment_failure", label: t("Accident déversement") },
      { value: "purifier", label: t("Épurateur") },
      {
        value: "injection",
        label: t(
          "Poste d'injection (autre que problématiques de saturation des réseaux)"
        ),
      },
      { value: "intrants", label: t("Intrants") },
      { value: "other", label: t("Autres (à préciser)") },
    ],
    [t]
  )

  return (
    <EditableCard
      title={t("Dysfonctionnements")}
      readOnly={!isInDeclarationPeriod}
    >
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={() => saveEnergy()}>
          <Grid cols={2} gap="lg">
            <RadioGroup
              readOnly={!isEditing}
              label={t("Y'a t-il eu des dysfonctionnements ?")}
              options={getYesNoOptions()}
              orientation="horizontal"
              required
            />
            <NumberInput
              readOnly={!isEditing}
              label={t("Durée cumulée du dysfonctionnement (en jours)")}
              required
            />
            <RadioGroup
              readOnly={!isEditing}
              label={t("Types de dysfonctionnement")}
              options={dysfunctionOptions}
              orientation="horizontal"
              required
            />
            <TextInput readOnly={!isEditing} label={t("Précisions")} required />
          </Grid>
          <Grid cols={2} gap="lg">
            <RadioGroup
              readOnly={!isEditing}
              label={t(
                "Difficultés pour l'injection dans le réseau de gaz en raison de périodes de saturation des réseaux"
              )}
              options={getYesNoOptions()}
              orientation="horizontal"
              required
            />
            <NumberInput
              readOnly={!isEditing}
              label={t("Nombre d’heures d’impossibilité d’injection (h)")}
              required
            />
          </Grid>
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
    </EditableCard>
  )
}
