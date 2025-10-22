import { Button } from "common/components/button2"
import { NumberInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { EditableCard } from "common/molecules/editable-card"
import { useTranslation } from "react-i18next"
import { useForm } from "common/components/form2"
import { DeepPartial } from "common/types"
import { BiomethaneEnergy, BiomethaneEnergyInputRequest } from "../types"
import { useSaveEnergy } from "../energy.hooks"
import { BiomethaneContract } from "biomethane/pages/contract/types"
import { isTariffReference2011Or2020 } from "biomethane/pages/contract"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration.provider"

type InjectedBiomethaneForm = DeepPartial<
  Pick<
    BiomethaneEnergyInputRequest,
    | "injected_biomethane_gwh_pcs_per_year"
    | "injected_biomethane_nm3_per_year"
    | "injected_biomethane_ch4_rate_percent"
    | "injected_biomethane_pcs_kwh_per_nm3"
    | "operating_hours"
  >
>

export function InjectedBiomethane({
  energy,
  contract,
}: {
  energy?: BiomethaneEnergy
  contract?: BiomethaneContract
}) {
  const { t } = useTranslation()
  const { bind, value } = useForm<InjectedBiomethaneForm>(energy ?? {})
  const saveEnergy = useSaveEnergy()
  const { canEditDeclaration } = useAnnualDeclaration()

  const handleSave = async () => saveEnergy.execute(value)

  return (
    <EditableCard
      title={t("Biométhane injecté dans le réseau")}
      description={t(
        "Ces informations concernent la production finale de biométhane de votre installation"
      )}
      readOnly={!canEditDeclaration}
    >
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={handleSave}>
          <NumberInput
            readOnly={!isEditing}
            label={t("Quantité de biométhane injecté (GWhPCS/an)")}
            type="number"
            {...bind("injected_biomethane_gwh_pcs_per_year")}
            required
          />
          <Grid cols={2} gap="lg">
            {isTariffReference2011Or2020(contract?.tariff_reference) && (
              <NumberInput
                readOnly={!isEditing}
                label={t("Quantité de biométhane injecté (Nm3/an)")}
                type="number"
                {...bind("injected_biomethane_nm3_per_year")}
                required
              />
            )}

            <NumberInput
              readOnly={!isEditing}
              label={t("Taux de CH4 dans le biométhane injecté (%)")}
              hintText={t("Valeur moyenne de l'année de déclaration")}
              type="number"
              min={0}
              max={100}
              {...bind("injected_biomethane_ch4_rate_percent")}
              required
            />
            <NumberInput
              readOnly={!isEditing}
              label={t("PCS du biométhane injecté (kWh/Nm3)")}
              hintText={t("Valeur moyenne de l'année de déclaration")}
              type="number"
              {...bind("injected_biomethane_pcs_kwh_per_nm3")}
              required
            />
            <NumberInput
              readOnly={!isEditing}
              label={t("Nombre d'heures de fonctionnement (h)")}
              hintText={t(
                "Fonctionnement à plein régime (à la capacité maximale inscrite dans le contrat)"
              )}
              type="number"
              {...bind("operating_hours")}
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
