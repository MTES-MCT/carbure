import { getCurrentAnnualDeclarationOk } from "biomethane/tests/api"
import { AnnualDeclarationProvider } from "./annual-declaration.provider"
import { StoryFn } from "@storybook/react"

export const AnnualDeclarationStoryUtils = {
  parameters: {
    msw: {
      handlers: [getCurrentAnnualDeclarationOk],
    },
    mockingDate: new Date(2025, 2, 1),
  },
  decorators: [
    (Story: StoryFn) => (
      <AnnualDeclarationProvider>
        <Story />
      </AnnualDeclarationProvider>
    ),
  ],
}
