import { AnnualDeclarationProvider } from "biomethane/providers/annual-declaration"
import { Outlet } from "react-router-dom"

export const AnnualDeclarationLayout = () => {
  return (
    <AnnualDeclarationProvider>
      <Outlet />
    </AnnualDeclarationProvider>
  )
}
