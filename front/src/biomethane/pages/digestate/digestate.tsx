import { BiomethanePageHeader } from "biomethane/layouts/page-header"
import { useParams } from "react-router-dom"
import { getDigestate, getYears } from "./api"
import useYears from "common/hooks/years-2"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { InjectionSite } from "./components/injection-site"
import { SpreadingDistance } from "./components/spreading-distance"
import { useProductionUnit } from "../production/production.hooks"
import { DigestateValorizationMethods } from "../production/types"
import { Spreading } from "./components/spreading"
import { DigestateProvider } from "./digestate.hooks"
import { LoaderOverlay } from "common/components/scaffold"

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

  if (loading) return <LoaderOverlay />

  return (
    <DigestateProvider year={years.selected}>
      <BiomethanePageHeader
        selectedYear={parseInt(year!)}
        yearsOptions={years.options}
        status={BiomethaneDigestateStatus.PENDING}
      >
        <InjectionSite digestate={digestate?.data} />
        {productionUnit?.digestate_valorization_methods?.includes(
          DigestateValorizationMethods.SPREADING
        ) && (
          <>
            <SpreadingDistance digestate={digestate?.data} />
            <Spreading digestate={digestate?.data} year={years.selected} />
          </>
        )}
      </BiomethanePageHeader>
    </DigestateProvider>
  )
}
