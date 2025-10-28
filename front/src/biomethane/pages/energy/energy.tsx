import useEntity from "common/hooks/entity"
import { useTranslation } from "react-i18next"
import { getEnergy } from "./api"
import { useQuery } from "common/hooks/async"
import { usePrivateNavigation } from "common/layouts/navigation"
import { SettingsNotFilled } from "biomethane/layouts/settings-not-filled"
import { LoaderOverlay } from "common/components/scaffold"
import { useGetContractInfos } from "../contract/contract.hooks"
import { InjectedBiomethane } from "./components/injected-biomethane"
import { BiogasProduction } from "./components/biogas-production"
import { useProductionUnit } from "../production/production.hooks"
import { EnergyEfficiency } from "./components/energy-efficiency"
import { InstallationEnergyNeeds } from "./components/installation-energy-needs"
import { MonthlyBiomethaneInjection } from "./components/monthy-biomethane-injection/monthly-biomethane-injection"
import { isTariffReference2011Or2020 } from "../contract"
import { Acceptability } from "./components/acceptability"
import { Malfunction } from "./components/malfunction"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"

export const Energy = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { selectedYear } = useAnnualDeclaration()
  const { result: contract } = useGetContractInfos()
  const { result: productionUnit } = useProductionUnit()
  const { result: energy, loading } = useQuery(getEnergy, {
    key: "energy",
    params: [entity.id, selectedYear],
  })

  usePrivateNavigation(t("Énergie"))

  if (loading && !energy) return <LoaderOverlay />

  if (!loading && contract === undefined) {
    return <SettingsNotFilled />
  }
  return (
    <>
      <InjectedBiomethane energy={energy} contract={contract} />
      <BiogasProduction energy={energy} productionUnit={productionUnit} />
      <InstallationEnergyNeeds energy={energy} contract={contract} />
      <EnergyEfficiency energy={energy} contract={contract} />
      {isTariffReference2011Or2020(contract?.tariff_reference) && (
        <MonthlyBiomethaneInjection energy={energy} />
      )}
      <Acceptability energy={energy} />
      <Malfunction energy={energy} />
    </>
  )
}
