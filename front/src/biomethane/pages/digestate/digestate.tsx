import { BiomethanePageHeader } from "biomethane/layouts/page-header"
import { useParams } from "react-router-dom"
import { getYears } from "./api"
import useYears from "common/hooks/years-2"

enum BiomethaneDigestateStatus {
  PENDING = "pending",
  VALIDATED = "validated",
}

export const Digestate = () => {
  const { year } = useParams<{ year: string }>()
  const years = useYears("biomethane/digestate", getYears)

  return (
    <BiomethanePageHeader
      selectedYear={parseInt(year!)}
      yearsOptions={years.options}
      status={BiomethaneDigestateStatus.PENDING}
    >
      contenu test
    </BiomethanePageHeader>
  )
}
