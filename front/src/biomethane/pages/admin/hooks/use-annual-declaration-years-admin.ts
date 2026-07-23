import useYears from "common/hooks/years-2"

export const getAnnualDeclarationYearsAdmin = () => {
  const currentYear = new Date().getFullYear()
  const startYear = 2025
  const endYear = currentYear > startYear ? currentYear - 1 : startYear

  return Array.from(
    { length: endYear - startYear + 1 },
    (_, i) => startYear + i
  )
}

export const annualDeclarationYearsAdmin = getAnnualDeclarationYearsAdmin()
export const lastAnnualDeclarationYearAdmin = annualDeclarationYearsAdmin.at(-1)

/**
 * Get years from 2025 (the first year of the biomethane module), to N-1 (the current year - 1)
 */
export const useAnnualDeclarationYearsAdmin = (urlRoot: string) =>
  useYears(
    urlRoot,
    () => {
      return Promise.resolve({
        data: annualDeclarationYearsAdmin,
        response: new Response(),
      })
    },
    { readOnly: false, withCurrentYearIfEmpty: false }
  )
