import { getDeclarationPeriodYears } from "accounting/api/api"
import useEntity from "common/hooks/entity"
import useYears from "common/hooks/years-2"

export const useAnnualDeclarationTiruertYears = () => {
  const entity = useEntity()

  return useYears(
    "teneur",
    () =>
      getDeclarationPeriodYears(entity.id).then((res) => ({
        ...res,
        data: res.data?.years ?? [],
      })),

    { readOnly: true, withCurrentYearIfEmpty: false }
  )
}
