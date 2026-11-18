import { useTranslation } from "react-i18next"
import useEntity from "common/hooks/entity"
import { LoaderOverlay } from "common/components/scaffold"
import {
  useEnergyInstallation,
  useSaveEnergyInstallation,
} from "./energy-installation.hooks"
import { GeneralCard } from "./components/general-card"
import { IcpeCard } from "./components/icpe-card"

export function EnergyInstallation() {
  const entity = useEntity()
  const { t } = useTranslation()
  const { result, loading, error } = useEnergyInstallation()
  const saveInstallation = useSaveEnergyInstallation()

  if (loading && !result) return <LoaderOverlay />
  if (error && !result)
    return <p>{t("Impossible de charger l'installation.")}</p>

  const installation = result?.data ?? {}

  const generalKey = JSON.stringify([
    installation.production_type,
    installation.heat_type,
    installation.commissioning_date,
    installation.useful_temperature,
    installation.electrical_efficiency,
    installation.thermal_efficiency,
  ])

  const icpeKey = JSON.stringify([
    installation.icpe_number,
    installation.icpe_regime,
  ])

  return (
    <>
      <GeneralCard
        key={generalKey}
        installation={installation}
        readOnly={!entity.canWrite()}
        save={saveInstallation.execute}
        loading={saveInstallation.loading}
      />
      <IcpeCard
        key={icpeKey}
        installation={installation}
        readOnly={!entity.canWrite()}
        save={saveInstallation.execute}
        loading={saveInstallation.loading}
      />
    </>
  )
}
