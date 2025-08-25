import { BiomethanePageHeader } from "biomethane/layouts/page-header"
import { useParams } from "react-router-dom"
import { getDigestate, getYears } from "./api"
import useYears from "common/hooks/years-2"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { InjectionSite } from "./components/injection-site"
import { SpreadingDistance } from "./components/spreading-distance"

enum BiomethaneDigestateStatus {
  PENDING = "pending",
  VALIDATED = "validated",
}

export const Digestate = () => {
  const entity = useEntity()
  const { year } = useParams<{ year: string }>()
  const years = useYears("biomethane/digestate", getYears)
  const { result: digestate } = useQuery(getDigestate, {
    key: "digestate",
    params: [entity.id, years.selected],
  })

  return (
    <BiomethanePageHeader
      selectedYear={parseInt(year!)}
      yearsOptions={years.options}
      status={BiomethaneDigestateStatus.PENDING}
    >
      <InjectionSite digestate={digestate?.data} />
      <SpreadingDistance digestate={digestate?.data} />
    </BiomethanePageHeader>
  )
}
