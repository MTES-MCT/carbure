/**
 * Determines the current declaration interval based on the current date.
 *
 * The declaration period runs from April 1st to March 31st of the following year.
 * The year being declared depends on the current month:
 * - If current month is January-March: declare for the previous year
 * - If current month is April-December: declare for the current year
 *
 * @param currentDate - The date to calculate the declaration interval from. Defaults to current date.
 * @returns An object containing the start date, end date, and declaration year
 *
 * @example
 * // On August 21, 2025 - declare for 2025
 * getDeclarationInterval(new Date(2025, 7, 21))
 * // Returns: { startDate: 2025-04-01, endDate: 2026-03-31, year: 2025 }
 *
 * @example
 * // On January 12, 2026 - declare for 2025
 * getDeclarationInterval(new Date(2026, 0, 12))
 * // Returns: { startDate: 2025-04-01, endDate: 2026-03-31, year: 2025 }
 *
 * @example
 * // On May 12, 2026 - declare for 2026
 * getDeclarationInterval(new Date(2026, 4, 12))
 * // Returns: { startDate: 2026-04-01, endDate: 2027-03-31, year: 2026 }
 */
export function getDeclarationInterval(currentDate: Date = new Date()) {
  const currentYear = currentDate.getFullYear()
  const currentMonth = currentDate.getMonth()

  const declarationYear = currentMonth < 3 ? currentYear - 1 : currentYear

  const startDate = new Date(declarationYear, 3, 1)
  const endDate = new Date(declarationYear + 1, 2, 31)

  return {
    startDate,
    endDate,
    year: declarationYear,
  }
}

export const declarationInterval = getDeclarationInterval()
