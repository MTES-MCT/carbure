import {
  AnnualDeclarationProvider,
  useAnnualDeclaration,
} from "biomethane/providers/annual-declaration"
import { Outlet } from "react-router-dom"
import { BiomethanePageHeader } from "./page-header"
import { DeclarationNotFound } from "biomethane/components/declaration-not-found"

export const AnnualDeclarationLayoutComponent = () => {
  const { currentAnnualDeclaration } = useAnnualDeclaration()

  if (currentAnnualDeclaration === undefined) return <DeclarationNotFound />

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
