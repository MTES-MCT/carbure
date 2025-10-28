import { Button } from "common/components/button2"
import { Checkbox, TextInput } from "common/components/inputs2"
import { ManagedEditableCard } from "common/molecules/editable-card/managed-editable-card"
import { useTranslation } from "react-i18next"
import { useFormContext } from "common/components/form2"
import { DeepPartial } from "common/types"
import { BiomethaneEnergyInputRequest } from "../types"
import { useSaveEnergy } from "../energy.hooks"
import {
  BiomethaneContract,
  TariffReference,
} from "biomethane/pages/contract/types"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { EditableCard } from "common/molecules/editable-card"

type InstallationEnergyNeedsForm = DeepPartial<
  Pick<
    BiomethaneEnergyInputRequest,
    | "attest_no_fossil_for_digester_heating_and_purification"
    | "energy_used_for_digester_heating"
    | "fossil_details_for_digester_heating"
    | "attest_no_fossil_for_installation_needs"
    | "energy_used_for_installation_needs"
    | "fossil_details_for_installation_needs"
  >
>

const extractValues = (energy?: InstallationEnergyNeedsForm) => {
  return {
    attest_no_fossil_for_digester_heating_and_purification:
      energy?.attest_no_fossil_for_digester_heating_and_purification,
    energy_used_for_digester_heating: energy?.energy_used_for_digester_heating,
    fossil_details_for_digester_heating:
      energy?.fossil_details_for_digester_heating,
    attest_no_fossil_for_installation_needs:
      energy?.attest_no_fossil_for_installation_needs,
    energy_used_for_installation_needs:
      energy?.energy_used_for_installation_needs,
    fossil_details_for_installation_needs:
      energy?.fossil_details_for_installation_needs,
  }
}
export function InstallationEnergyNeeds({
  contract,
}: {
  contract?: BiomethaneContract
}) {
  const { t } = useTranslation()

  const { bind, value } = useFormContext<InstallationEnergyNeedsForm>()
  const saveEnergy = useSaveEnergy()
  const { canEditDeclaration } = useAnnualDeclaration()

  const handleSubmit = async () => saveEnergy.execute(extractValues(value))

  const isTariffReference2023 =
    contract?.tariff_reference === TariffReference.Value2023

  return (
    <ManagedEditableCard
      sectionId="installation-energy-needs"
      title={t(
        "Nature de l’énergie utilisée pour les besoins de l'installation"
      )}
      readOnly={!canEditDeclaration}
    >
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={handleSubmit}>
          {!isTariffReference2023 && (
            <>
              <Checkbox
                readOnly={!isEditing}
                hintText={t(
                  "Pour une installation de méthanisation ainsi qu’à l’épuration du biogaz et à l’oxydation des évents"
                )}
                legend={t("Besoins en énergie liés au chauffage du digesteur")}
                label={t(
                  "J'atteste que les besoins en énergie cités ci-dessus ne sont pas satisfaits par une énergie d’origine fossile."
                )}
                {...bind(
                  "attest_no_fossil_for_digester_heating_and_purification"
                )}
              />
              <TextInput
                readOnly={!isEditing}
                label={t("Énergie utilisée pour le chauffage du digesteur")}
                {...bind("energy_used_for_digester_heating")}
                required
              />
              {!value.attest_no_fossil_for_digester_heating_and_purification && (
                <TextInput
                  readOnly={!isEditing}
                  label={t(
                    "Précisions (si utilisation d’énergie d’origine fossile)"
                  )}
                  {...bind("fossil_details_for_digester_heating")}
                  required
                />
              )}
            </>
          )}
          {isTariffReference2023 && (
            <>
              <Checkbox
                readOnly={!isEditing}
                hintText={t(
                  "Notamment liés à la pasteurisation, l’hygiénisation et le prétraitement des intrants, le chauffage du digesteur et l’épuration du biogaz"
                )}
                legend={t(
                  "Besoins en énergie de l’installation de production de biométhane"
                )}
                label={t(
                  "J'atteste que les besoins en énergie cités ci-dessus ne sont pas satisfaits par une énergie d’origine fossile."
                )}
                {...bind("attest_no_fossil_for_installation_needs")}
              />
              <TextInput
                readOnly={!isEditing}
                label={t(
                  "Énergie utilisée pour la pasteurisation, l'hygiénisation et le prétraitement des intrants, le chauffage du digesteur et l’épuration du biogaz "
                )}
                {...bind("energy_used_for_installation_needs")}
                required
              />
              {!value.attest_no_fossil_for_installation_needs && (
                <TextInput
                  readOnly={!isEditing}
                  label={t(
                    "Précisions (si utilisation d’énergie d’origine fossile)"
                  )}
                  {...bind("fossil_details_for_installation_needs")}
                  required
                />
              )}
            </>
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
