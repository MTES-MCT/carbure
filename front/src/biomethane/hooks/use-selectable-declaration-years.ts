import useYears from "common/hooks/years-2"

export const getSelectableDeclarationYears = () => {
  const currentYear = new Date().getFullYear()
  const startYear = 2025
  const endYear = currentYear > startYear ? currentYear - 1 : startYear

  return Array.from(
    { length: endYear - startYear + 1 },
    (_, index) => startYear + index
  )
}

export const selectableDeclarationYears = getSelectableDeclarationYears()
export const lastSelectableDeclarationYear = selectableDeclarationYears.at(-1)

export const useSelectableDeclarationYears = (urlRoot: string) =>
  useYears(
    urlRoot,
    () =>
      Promise.resolve({
        data: selectableDeclarationYears,
        response: new Response(),
      }),
    { readOnly: false, withCurrentYearIfEmpty: false }
  )
