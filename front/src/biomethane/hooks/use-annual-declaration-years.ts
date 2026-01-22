import { getAnnualDeclarationYears } from "biomethane/api"
import useEntity from "common/hooks/entity"
import useYears from "common/hooks/years-2"
import { ExternalAdminPages } from "common/types"

const getYears = () => {
  const currentYear = new Date().getFullYear()
  const startYear = 2025
  const endYear = currentYear > startYear ? currentYear - 1 : startYear
  return Array.from(
    { length: endYear - startYear + 1 },
    (_, i) => startYear + i
  )
}
/**
 * Get years from 2025 (the first year of the biomethane module), to N-1 (the current year - 1)
 */
export const useAnnualDeclarationYears = () => {
  const entity = useEntity()

  return useYears(
    "biomethane",
    () => {
      // For DREAL admins, we need to set the years from the beginning of the biomethane module
      if (entity.hasAdminRight(ExternalAdminPages.DREAL)) {
        return Promise.resolve({
          data: getYears(),
          response: new Response(),
        })
      }
      // For biomethane producers, we need to fetch the years from the API
      return getAnnualDeclarationYears(entity.id).then((res) => ({
        ...res,
        data: res.data ?? [],
      }))
    },
    { readOnly: true, withCurrentYearIfEmpty: false }
  )
}
