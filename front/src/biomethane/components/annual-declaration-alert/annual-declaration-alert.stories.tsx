import type { Meta, StoryObj } from "@storybook/react"
import { AnnualDeclarationAlert } from "./annual-declaration-alert"
import { AnnualDeclarationStatus } from "biomethane/types"
import {
  AnnualDeclarationContextProvider,
  createMockAnnualDeclaration,
} from "./annual-declaration-alert.stories.utils"
import { expect, within } from "@storybook/test"

const meta: Meta<typeof AnnualDeclarationAlert> = {
  component: AnnualDeclarationAlert,
  title: "modules/biomethane/components/annual-declaration-alert",
  decorators: [
    (Story) => (
      <AnnualDeclarationContextProvider
        selectedYear={2024}
        currentAnnualDeclaration={createMockAnnualDeclaration(
          AnnualDeclarationStatus.IN_PROGRESS
        )}
        isInDeclarationPeriod={false}
        isDeclarationValidated={false}
        canEditDeclaration={false}
      >
        <Story />
      </AnnualDeclarationContextProvider>
    ),
  ],
}

export default meta

type Story = StoryObj<typeof AnnualDeclarationAlert>

// Case 1: Not in declaration period - should not display anything
export const Default: Story = {
  parameters: {
    chromatic: { disableSnapshot: true },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await expect(canvas.queryByTestId("annual-declaration-alert")).toBeNull()
  },
}

// Case 2: In declaration period but declaration in progress - should not display anything
export const DeclarationInProgress: Story = {
  ...Default,
  decorators: [
    (Story) => (
      <AnnualDeclarationContextProvider
        currentAnnualDeclaration={createMockAnnualDeclaration(
          AnnualDeclarationStatus.IN_PROGRESS
        )}
        selectedYear={2024}
        isInDeclarationPeriod
        isDeclarationValidated={false}
        canEditDeclaration={false}
      >
        <Story />
      </AnnualDeclarationContextProvider>
    ),
  ],
}

// Case 3: In declaration period and declaration already submitted - should display alert
export const DeclarationAlreadySubmitted: Story = {
  decorators: [
    (Story) => (
      <AnnualDeclarationContextProvider
        currentAnnualDeclaration={createMockAnnualDeclaration(
          AnnualDeclarationStatus.DECLARED
        )}
        selectedYear={2024}
        isInDeclarationPeriod
        isDeclarationValidated={true}
        canEditDeclaration={false}
      >
        <Story />
      </AnnualDeclarationContextProvider>
    ),
  ],
}
