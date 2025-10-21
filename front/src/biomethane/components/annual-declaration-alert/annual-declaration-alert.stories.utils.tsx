import {
  AnnualDeclarationContext,
  AnnualDeclarationContextValue,
} from "biomethane/providers/annual-declaration.provider"
import { AnnualDeclaration, AnnualDeclarationStatus } from "biomethane/types"

export const createMockAnnualDeclaration = (
  status: AnnualDeclarationStatus,
  year: number = 2024
): AnnualDeclaration => ({
  year,
  status,
  missing_fields: {
    digestate_missing_fields: [],
    energy_missing_fields: [],
  },
  is_complete: false,
})

export const AnnualDeclarationContextProvider = ({
  children,
  ...props
}: {
  children: React.ReactNode
} & AnnualDeclarationContextValue) => {
  return (
    <AnnualDeclarationContext.Provider value={props}>
      {children}
    </AnnualDeclarationContext.Provider>
  )
}
