import { getAnnualDeclarationYears } from "biomethane/api"
import { AnnualDeclarationProvider } from "biomethane/providers/annual-declaration"
import useYears from "common/hooks/years-2"
import { Outlet } from "react-router-dom"

export const AnnualDeclarationLayout = () => {
  const years = useYears("biomethane", getAnnualDeclarationYears)

  return (
    <AnnualDeclarationProvider>
      <Outlet context={{ years: years.selected }} />
    </AnnualDeclarationProvider>
  )
}
