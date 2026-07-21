import { getDeclarationPeriodYears } from "accounting/api/api"
import useEntity from "common/hooks/entity"
import useYears from "common/hooks/years-2"

export const useAnnualDeclarationTiruertYears = (urlRoot: string) => {
  const entity = useEntity()

  return useYears(urlRoot, () =>
    getDeclarationPeriodYears(entity.id).then((res) => ({
      ...res,
      data: res.data?.years ?? [],
    }))
  )
}
