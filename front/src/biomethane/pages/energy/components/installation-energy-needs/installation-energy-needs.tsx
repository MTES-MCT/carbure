import { Button } from "common/components/button2"
import { Checkbox, TextInput } from "common/components/inputs2"
import { ManagedEditableCard } from "common/molecules/editable-card/managed-editable-card"
import { useTranslation } from "react-i18next"
import { useFormContext } from "common/components/form2"
import { BiomethaneEnergyInputRequest, EnergyType } from "../../types"
import { useSaveEnergy } from "../../energy.hooks"
import { BiomethaneContract } from "biomethane/pages/contract/types"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { useAttestNoFossilForEnergy } from "./installation-energy-needs.hooks"
import { EnergyTypes } from "./energy-types"

type InstallationEnergyNeedsForm = Pick<
  BiomethaneEnergyInputRequest,
  "attest_no_fossil_for_energy" | "energy_types" | "energy_details"
>

const extractValues = (energy?: InstallationEnergyNeedsForm) => {
  return {
    attest_no_fossil_for_energy: energy?.attest_no_fossil_for_energy,
    energy_types: energy?.energy_types ?? [],
    energy_details: energy?.energy_details,
  }
}
export function InstallationEnergyNeeds({
  contract,
}: {
  contract?: BiomethaneContract
}) {
  const { t } = useTranslation()

  const form = useFormContext<InstallationEnergyNeedsForm>()
  const { bind, value } = form
  const saveEnergy = useSaveEnergy()
  const { canEditDeclaration } = useAnnualDeclaration()
  const attestNoFossilForEnergyTexts = useAttestNoFossilForEnergy(
    contract?.tariff_reference
  )

  const handleSubmit = async () => saveEnergy.execute(extractValues(value))

  const displayDetailsField = value.energy_types?.some((type) =>
    [EnergyType.FOSSIL, EnergyType.OTHER_RENEWABLE, EnergyType.OTHER].includes(
      type
    )
  )
  return (
    <ManagedEditableCard
      sectionId="installation-energy-needs"
      title={t(
        "Nature de l’énergie utilisée pour les besoins de l'installation"
      )}
      readOnly={!canEditDeclaration}
    >
      {({ isEditing }) => (
        <ManagedEditableCard.Form onSubmit={handleSubmit} form={form}>
          <Checkbox
            readOnly={!isEditing}
            {...attestNoFossilForEnergyTexts}
            {...bind("attest_no_fossil_for_energy")}
          />
          <EnergyTypes contract={contract} isReadOnly={!isEditing} />
          {displayDetailsField && (
            <TextInput
              readOnly={!isEditing}
              label={t("Précisions")}
              {...bind("energy_details")}
              required
            />
          )}
          {/* {!isTariffReference2023 && (
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
                label={t(
                  "Type d'énergie utilisée pour le chauffage du digesteur"
                )}
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
                  "Type d'énergie utilisée pour la pasteurisation, l'hygiénisation et le prétraitement des intrants, le chauffage du digesteur et l’épuration du biogaz "
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
          )} */}

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
        </ManagedEditableCard.Form>
      )}
    </ManagedEditableCard>
  )
}
