import type { Meta, StoryObj } from "@storybook/react"
import mswHandlers from "@storybook/mocks"
import { CompanyRegistrationDialog } from "./registration-dialog"
import {
  fillSirenAndWaitForResult,
  searchCompanyHandlers,
  searchCompanyOneEntityInMeta,
  searchCompanySeveralEntitiesInMeta,
} from "./registration-dialog.stories.utils"

const meta: Meta<typeof CompanyRegistrationDialog> = {
  component: CompanyRegistrationDialog,
  title: "modules/companies/components/RegistrationDialog",
  parameters: {
    msw: {
      handlers: [...mswHandlers, ...searchCompanyHandlers],
    },
  },
}

type Story = StoryObj<typeof CompanyRegistrationDialog>

export default meta

export const Default: Story = {}

export const SirenWithOneExistingEntity: Story = {
  parameters: {
    msw: {
      handlers: [...mswHandlers, searchCompanyOneEntityInMeta],
    },
  },
  play: async ({ canvasElement }) => {
    await fillSirenAndWaitForResult(canvasElement)
  },
}

export const SirenWithSeveralExistingEntities: Story = {
  parameters: {
    msw: {
      handlers: [...mswHandlers, searchCompanySeveralEntitiesInMeta],
    },
  },
  play: async ({ canvasElement }) => {
    await fillSirenAndWaitForResult(canvasElement)
  },
}
