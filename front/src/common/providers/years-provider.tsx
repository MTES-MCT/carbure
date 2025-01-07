import React, { createContext, useContext, useState, useMemo } from "react"

const currentYear = new Date().getFullYear()
/**
 * This provider is used to share the selected year between each page and the sidebar
 */
type YearContextType = {
  selectedYear: number
  // root is the root of the page, used to determine if the selected year should be the current year or the selected year
  root: string
  setSelectedYear: (year: number) => void
  setRoot: (root: string) => void
}

const YearContext = createContext<YearContextType | undefined>({
  selectedYear: currentYear,
  root: "",
  setSelectedYear: (year) => year,
  setRoot: (root) => root,
})

export const YearsProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [selectedYear, setSelectedYear] = useState(currentYear)
  const [root, setRoot] = useState("")
  const value = useMemo(
    () => ({
      selectedYear,
      setSelectedYear,
      root,
      setRoot,
    }),
    [selectedYear, setSelectedYear, root, setRoot]
  )

  return <YearContext.Provider value={value}>{children}</YearContext.Provider>
}

export function useYearsProvider() {
  const year = useContext(YearContext)
  if (year === undefined) throw new Error("Year context is not defined")
  return year
}
