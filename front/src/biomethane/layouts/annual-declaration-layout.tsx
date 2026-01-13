import {
  AnnualDeclarationProvider,
  useAnnualDeclaration,
} from "biomethane/providers/annual-declaration"
import { Navigate, Outlet } from "react-router-dom"
import { BiomethanePageHeader } from "./page-header"
import { useRoutes } from "common/hooks/routes"

export const AnnualDeclarationLayoutComponent = () => {
  const { currentAnnualDeclaration } = useAnnualDeclaration()
  const biomethaneRoutes = useRoutes().BIOMETHANE()

  if (currentAnnualDeclaration === undefined)
    return <Navigate to={`${biomethaneRoutes.ROOT}/declaration-not-found`} />

  return (
    <BiomethanePageHeader>
      <Outlet />
    </BiomethanePageHeader>
  )
}

export const AnnualDeclarationLayout = () => {
  return (
    <AnnualDeclarationProvider>
      <AnnualDeclarationLayoutComponent />
    </AnnualDeclarationProvider>
  )
}
