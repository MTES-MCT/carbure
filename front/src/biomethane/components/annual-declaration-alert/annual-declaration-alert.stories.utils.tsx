import { StoryFn } from "@storybook/react"
import {
  AnnualDeclarationContext,
  AnnualDeclarationContextValue,
} from "biomethane/providers/annual-declaration"
import { currentAnnualDeclaration } from "biomethane/tests/data"
import { AnnualDeclaration, AnnualDeclarationStatus } from "biomethane/types"

export const createMockAnnualDeclaration = (
  status: AnnualDeclarationStatus,
  year: number = 2024
): AnnualDeclaration => ({
  ...currentAnnualDeclaration,
  year,
  status,
  is_complete: false,
})

export const generateAnnualDeclarationContextProvider = (
  props: Partial<AnnualDeclarationContextValue> = {}
) => {
  const defaultProps: AnnualDeclarationContextValue = {
    selectedYear: 2024,
    currentAnnualDeclaration: createMockAnnualDeclaration(
      AnnualDeclarationStatus.IN_PROGRESS
    ),
    isInDeclarationPeriod: false,
    isDeclarationValidated: false,
    canEditDeclaration: false,
    hasAnnualDeclarationMissingObjects: false,
    hasAtLeastOneSupplyInput: false,
    currentAnnualDeclarationKey: "current-annual-declaration-2024",
  }
  const mergedProps = { ...defaultProps, ...props }

  return (Story: StoryFn) => (
    <AnnualDeclarationContext.Provider value={mergedProps}>
      <Story />
    </AnnualDeclarationContext.Provider>
  )
}
