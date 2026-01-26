import { getAnnualDeclarationYears } from "biomethane/api"
import useEntity from "common/hooks/entity"
import useYears from "common/hooks/years-2"

export const useAnnualDeclarationYears = () => {
  const entity = useEntity()

  return useYears(
    "biomethane",
    () =>
      getAnnualDeclarationYears(entity.id).then((res) => ({
        ...res,
        data: res.data ?? [],
      })),

    // If the user is a biomethane producer, we just need to fill the select with the years from the API, without redirecting to the last year
    { readOnly: true, withCurrentYearIfEmpty: false }
  )
}
