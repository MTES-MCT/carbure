import { AnnualDeclarationProvider } from "biomethane/providers/annual-declaration"
import { Outlet } from "react-router-dom"
import { BiomethanePageHeader } from "./page-header"

export const AnnualDeclarationLayout = () => {
  return (
    <AnnualDeclarationProvider>
      <BiomethanePageHeader>
        <Outlet />
      </BiomethanePageHeader>
    </AnnualDeclarationProvider>
  )
}
