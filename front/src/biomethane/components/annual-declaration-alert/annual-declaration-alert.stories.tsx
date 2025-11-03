import type { Meta, StoryObj } from "@storybook/react"
import { AnnualDeclarationAlert } from "./annual-declaration-alert"
import {
  createMockAnnualDeclaration,
  generateAnnualDeclarationContextProvider,
} from "./annual-declaration-alert.stories.utils"
import { expect, within } from "@storybook/test"
import { AnnualDeclarationStatus } from "biomethane/types"

const meta: Meta<typeof AnnualDeclarationAlert> = {
  component: AnnualDeclarationAlert,
  title: "modules/biomethane/components/annual-declaration-alert",
  decorators: [generateAnnualDeclarationContextProvider()],
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
    generateAnnualDeclarationContextProvider({
      isInDeclarationPeriod: true,
    }),
  ],
}

// Case 3: In declaration period and declaration already submitted - should display alert
export const DeclarationAlreadySubmitted: Story = {
  decorators: [
    generateAnnualDeclarationContextProvider({
      isInDeclarationPeriod: true,
      isDeclarationValidated: true,
      currentAnnualDeclaration: createMockAnnualDeclaration(
        AnnualDeclarationStatus.DECLARED
      ),
    }),
  ],
}
