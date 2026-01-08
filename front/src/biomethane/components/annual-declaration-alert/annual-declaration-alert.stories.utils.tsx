import { StoryFn } from "@storybook/react"
import {
  AnnualDeclarationContext,
  AnnualDeclarationContextValue,
} from "biomethane/providers/annual-declaration"
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
  }
  const mergedProps = { ...defaultProps, ...props }

  return (Story: StoryFn) => (
    <AnnualDeclarationContext.Provider value={mergedProps}>
      <Story />
    </AnnualDeclarationContext.Provider>
  )
}
