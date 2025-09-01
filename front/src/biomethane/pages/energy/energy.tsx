import { useNotify } from "common/components/notifications"
import useEntity from "common/hooks/entity"
import useYears from "common/hooks/years-2"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"
import { getEnergy, getYears, validateEnergy } from "./api"
import { useMutation, useQuery } from "common/hooks/async"
import { usePrivateNavigation } from "common/layouts/navigation"
import { SettingsNotFilled } from "biomethane/layouts/settings-not-filled"
import { LoaderOverlay } from "common/components/scaffold"
import { EnergyProvider } from "./energy.hooks"
import { BiomethanePageHeader } from "biomethane/layouts/page-header"
import { useGetContractInfos } from "../contract/contract.hooks"
import { InjectedBiomethane } from "./components/injected-biomethane"
import { BiogasProduction } from "./components/biogas-production"
import { useProductionUnit } from "../production/production.hooks"

export const Energy = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { year } = useParams<{ year: string }>()
  const notify = useNotify()
  const years = useYears("biomethane/energy", getYears)
  const { result: contract } = useGetContractInfos()
  const { result: productionUnit } = useProductionUnit()
  const { result: energy, loading } = useQuery(getEnergy, {
    key: "digestate",
    params: [entity.id, years.selected],
  })
  const validateEnergyMutation = useMutation(() => validateEnergy(entity.id), {
    invalidates: ["energy"],
    onSuccess: () => {
      notify(t("Les informations ont bien été validées."), {
        variant: "success",
      })
    },
  })

  usePrivateNavigation(t("Énergie"))

  if (loading) return <LoaderOverlay />

  if (!loading && contract === undefined) {
    return <SettingsNotFilled />
  }
  return (
    <EnergyProvider year={years.selected}>
      <BiomethanePageHeader
        selectedYear={parseInt(year!)}
        yearsOptions={years.options}
        status={energy?.status}
        onChangeYear={years.setYear}
        onConfirm={validateEnergyMutation.execute}
      >
        <InjectedBiomethane energy={energy} contract={contract} />
        <BiogasProduction energy={energy} productionUnit={productionUnit} />
      </BiomethanePageHeader>
    </EnergyProvider>
  )
}
