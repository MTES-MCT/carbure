import { AnnualDeclarationProvider } from "biomethane/providers/annual-declaration.provider"
import { Outlet } from "react-router-dom"

export const AnnualDeclarationLayout = () => {
  return (
    <AnnualDeclarationProvider>
      <Outlet />
    </AnnualDeclarationProvider>
  )
}
