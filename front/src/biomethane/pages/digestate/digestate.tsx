import { BiomethanePageHeader } from "biomethane/layouts/page-header"
import { useParams } from "react-router-dom"
import { getDigestate, getYears } from "./api"
import useYears from "common/hooks/years-2"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { InjectionSite } from "./components/injection-site"
import { SpreadingDistance } from "./components/spreading-distance"
import { useProductionUnit } from "../production/production.hooks"
import {
  DigestateValorizationMethods,
  SpreadingManagementMethods,
} from "../production/types"
import { Spreading } from "./components/spreading"
import { DigestateProvider } from "./digestate.hooks"
import { LoaderOverlay } from "common/components/scaffold"
import { SettingsNotFilled } from "biomethane/layouts/settings-not-filled"
import { Composting } from "./components/composting"
import { IncinerationLandfill } from "./components/incineration-landfill"
import { Sale } from "./components/sale"
import { useGetContractInfos } from "../contract/contract.hooks"

enum BiomethaneDigestateStatus {
  PENDING = "pending",
  VALIDATED = "validated",
}

export const Digestate = () => {
  const entity = useEntity()
  const { year } = useParams<{ year: string }>()
  const years = useYears("biomethane/digestate", getYears)
  const { result: digestate, loading } = useQuery(getDigestate, {
    key: "digestate",
    params: [entity.id, years.selected],
  })
  const { result: productionUnit } = useProductionUnit()
  const { result: contract } = useGetContractInfos()

  if (loading) return <LoaderOverlay />

  if (!loading && !productionUnit?.id) {
    return <SettingsNotFilled />
  }
  return (
    <DigestateProvider year={years.selected}>
      <BiomethanePageHeader
        selectedYear={parseInt(year!)}
        yearsOptions={years.options}
        status={BiomethaneDigestateStatus.PENDING}
      >
        {productionUnit && (
          <InjectionSite
            digestate={digestate?.data}
            productionUnit={productionUnit}
          />
        )}

        {productionUnit?.digestate_valorization_methods?.includes(
          DigestateValorizationMethods.SPREADING
        ) && (
          <>
            <SpreadingDistance digestate={digestate?.data} />
            <Spreading digestate={digestate?.data} year={years.selected} />
          </>
        )}

        {productionUnit?.digestate_valorization_methods?.includes(
          DigestateValorizationMethods.COMPOSTING
        ) && <Composting digestate={digestate?.data} />}

        {productionUnit?.digestate_valorization_methods?.includes(
          DigestateValorizationMethods.INCINERATION_LANDFILLING
        ) && (
          <IncinerationLandfill
            digestate={digestate?.data}
            contract={contract}
          />
        )}

        {productionUnit?.spreading_management_methods?.includes(
          SpreadingManagementMethods.SALE
        ) && <Sale digestate={digestate?.data} />}
      </BiomethanePageHeader>
    </DigestateProvider>
  )
}
