import { getDigestate } from "./api"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { Production } from "./components/production"
import { SpreadingDistance } from "./components/spreading-distance"
import { useProductionUnit } from "../production/production.hooks"
import {
  DigestateValorizationMethods,
  SpreadingManagementMethods,
} from "../production/types"
import { Spreading } from "./components/spreading"
import { LoaderOverlay } from "common/components/scaffold"
import { SettingsNotFilled } from "biomethane/layouts/settings-not-filled"
import { Composting } from "./components/composting"
import { IncinerationLandfill } from "./components/incineration-landfill"
import { Sale } from "./components/sale"
import { useGetContractInfos } from "../contract/contract.hooks"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { SectionsManagerProvider } from "common/providers/sections-manager.provider"

export const Digestate = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { selectedYear } = useAnnualDeclaration()

  const { result: digestate, loading } = useQuery(getDigestate, {
    key: "digestate",
    params: [entity.id, selectedYear],
  })

  const { result: productionUnit } = useProductionUnit()
  const { result: contract } = useGetContractInfos()

  usePrivateNavigation(t("Digestat"))

  if (loading && !digestate) return <LoaderOverlay />

  if (!loading && !productionUnit?.id) {
    return <SettingsNotFilled />
  }

  return (
    <SectionsManagerProvider>
      {productionUnit && (
        <Production
          digestate={digestate?.data}
          productionUnit={productionUnit}
        />
      )}

      {productionUnit?.digestate_valorization_methods?.includes(
        DigestateValorizationMethods.SPREADING
      ) && (
        <>
          <SpreadingDistance digestate={digestate?.data} />
          <Spreading digestate={digestate?.data} />
        </>
      )}

      {productionUnit?.digestate_valorization_methods?.includes(
        DigestateValorizationMethods.COMPOSTING
      ) && <Composting digestate={digestate?.data} />}

      {productionUnit?.digestate_valorization_methods?.includes(
        DigestateValorizationMethods.INCINERATION_LANDFILLING
      ) && (
        <IncinerationLandfill digestate={digestate?.data} contract={contract} />
      )}

      {productionUnit?.spreading_management_methods?.includes(
        SpreadingManagementMethods.SALE
      ) && <Sale digestate={digestate?.data} />}
    </SectionsManagerProvider>
  )
}
