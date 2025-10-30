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
import { SectionsManagerProvider } from "common/providers/sections-manager.provider"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { FormContext, useForm } from "common/components/form2"
import { BiomethaneEnergy } from "./types"
import { MissingFields } from "biomethane/components/missing-fields"
import { useMissingFields } from "biomethane/components/missing-fields/missing-fields.hooks"
import { BiomethanePageHeader } from "biomethane/layouts/page-header"

const EnergyPage = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const form = useForm<BiomethaneEnergy | undefined | object>(undefined)
  const { selectedYear } = useAnnualDeclaration()
  const { result: contract } = useGetContractInfos()
  const { result: productionUnit } = useProductionUnit()
  const { result: energy, loading } = useQuery(getEnergy, {
    key: "energy",
    params: [entity.id, selectedYear],
    onSuccess: (energy) => {
      form.setValue(energy)
    },
    onError: () => {
      // If the energy is not found, we need to set an empty object to the form
      form.setValue({})
    },
  })

  usePrivateNavigation(t("Énergie"))
  useMissingFields(form)

  if (loading && !energy) return <LoaderOverlay />

  if (!loading && contract === undefined) {
    return <SettingsNotFilled />
  }
  return (
    <BiomethanePageHeader>
      <FormContext.Provider value={form}>
        <MissingFields />
        <InjectedBiomethane contract={contract} />
        <BiogasProduction productionUnit={productionUnit} />
        <InstallationEnergyNeeds contract={contract} />
        <EnergyEfficiency energy={energy} contract={contract} />
        {isTariffReference2011Or2020(contract?.tariff_reference) && (
          <MonthlyBiomethaneInjection energy={energy} />
        )}
        <Acceptability />
        <Malfunction />
      </FormContext.Provider>
    </BiomethanePageHeader>
  )
}

export const Energy = () => {
  return (
    <SectionsManagerProvider>
      <EnergyPage />
    </SectionsManagerProvider>
  )
}
