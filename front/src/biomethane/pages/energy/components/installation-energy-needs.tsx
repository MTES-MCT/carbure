import { Button } from "common/components/button2"
import { Checkbox, TextInput } from "common/components/inputs2"
import { EditableCard } from "common/molecules/editable-card"
import { Trans, useTranslation } from "react-i18next"
import { useForm } from "common/components/form2"
import { DeepPartial } from "common/types"
import { BiomethaneEnergy, BiomethaneEnergyAddRequest } from "../types"
import { useEnergyContext } from "../energy.hooks"
import {
  BiomethaneContract,
  TariffReference,
} from "biomethane/pages/contract/types"

type InstallationEnergyNeedsForm = DeepPartial<
  Pick<
    BiomethaneEnergyAddRequest,
    | "attest_no_fossil_for_digester_heating_and_purification"
    | "energy_used_for_digester_heating"
    | "fossil_details_for_digester_heating"
    | "attest_no_fossil_for_installation_needs"
    | "energy_used_for_installation_needs"
    | "fossil_details_for_installation_needs"
  >
>

export function InstallationEnergyNeeds({
  energy,
  contract,
}: {
  energy?: BiomethaneEnergy
  contract?: BiomethaneContract
}) {
  const { t } = useTranslation()

  const { bind, value } = useForm<InstallationEnergyNeedsForm>(energy ?? {})
  const { saveEnergy, isInDeclarationPeriod } = useEnergyContext()

  const handleSubmit = async () => saveEnergy.execute(value)

  const isTariffReference2023 =
    contract?.tariff_reference === TariffReference.Value2023

  return (
    <EditableCard
      title={t(
        "Nature de l’énergie utilisée pour les besoins de l'installation"
      )}
      readOnly={!isInDeclarationPeriod}
    >
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={handleSubmit}>
          {!isTariffReference2023 && (
            <>
              <Checkbox
                readOnly={!isEditing}
                legend={t(
                  "Besoins en énergie liés au chauffage du digesteur pour une installation de méthanisation ainsi qu’à l’épuration du biogaz et à l’oxydation des évents"
                )}
                label={t(
                  "J'atteste que les besoins en énergie cités ci-dessus ne sont pas satisfaits par une énergie d’origine fossile."
                )}
                {...bind(
                  "attest_no_fossil_for_digester_heating_and_purification"
                )}
              />
              <Checkbox
                readOnly={!isEditing}
                label={
                  <span>
                    <Trans components={{ b: <b /> }}>
                      J'atteste que les besoins en énergie liés au chauffage du
                      digesteur pour une installation de méthanisation ainsi
                      qu’à l’épuration du biogaz et à l’oxydation des évents{" "}
                      <b>ne sont pas satisfaits</b> par une énergie d’origine
                      fossile.
                    </Trans>
                  </span>
                }
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
              <TextInput
                readOnly={!isEditing}
                label={t(
                  "Précisions (si utilisation d’énergie d’origine fossile)"
                )}
                {...bind("fossil_details_for_digester_heating")}
                required={
                  !value.attest_no_fossil_for_digester_heating_and_purification
                }
              />
            </>
          )}
          {isTariffReference2023 && (
            <>
              <Checkbox
                readOnly={!isEditing}
                legend={t(
                  "Besoins en énergie de l’installation de production de biométhane (notamment liés à la pasteurisation, l’hygiénisation et le prétraitement des intrants, le chauffage du digesteur et l’épuration du biogaz)"
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
              <TextInput
                readOnly={!isEditing}
                label={t(
                  "Précisions (si utilisation d’énergie d’origine fossile)"
                )}
                {...bind("fossil_details_for_installation_needs")}
                required={!value.fossil_details_for_installation_needs}
              />
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
    </EditableCard>
  )
}
