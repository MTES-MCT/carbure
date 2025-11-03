import type { Meta, StoryObj } from "@storybook/react"
import { AnnualDeclarationStoryUtils } from "biomethane/providers/annual-declaration/annual-declaration.stories.utils"
import { ContractInfos } from "./contract-infos"
import { contractData } from "../../tests/contract.data"
import { generateWatchedFieldsProvider } from "biomethane/providers/watched-fields/watched-fields.stories.utils"
import { updateContractOk } from "../../tests/api"
import { okEntitySearch } from "common/__test__/api"
import MOCKS from "@storybook/mocks"
import { InstallationCategory, TariffReference } from "../../types"
import { fireEvent, userEvent, waitFor, within } from "@storybook/test"

const meta: Meta<typeof ContractInfos> = {
  title: "modules/biomethane/pages/contract/components/ContractInfos",
  component: ContractInfos,
  ...AnnualDeclarationStoryUtils,
  parameters: {
    msw: {
      handlers: [
        ...MOCKS,
        ...AnnualDeclarationStoryUtils.parameters.msw.handlers,
        updateContractOk,
        okEntitySearch,
      ],
    },
  },
  decorators: [
    ...AnnualDeclarationStoryUtils.decorators,
    generateWatchedFieldsProvider([]),
  ],
}

export default meta

type Story = StoryObj<typeof ContractInfos>

// When the tariff reference is 2011 or 2020, CMAX field is displayed
export const WithCMAX: Story = {
  args: {
    contract: {
      ...contractData,
      tariff_reference: TariffReference.Value2011,
    },
  },
}

// When the CMAX is higher than the threshold, the RED II notice is displayed
export const CMAXHigherThanThreshold: Story = {
  args: {
    contract: {
      ...contractData,
      tariff_reference: TariffReference.Value2011,
      cmax: 1000,
    },
  },
}

// When the tariff reference is 2021 or 2023, PAP field is displayed
export const WithPAP: Story = {
  args: {
    contract: contractData,
  },
}

// When the PAP is higher than the threshold, the RED II notice is displayed
export const PAPHigherThanThreshold: Story = {
  args: {
    contract: {
      ...contractData,
      pap_contracted: 1000,
    },
  },
}

// When certain fields that conditionally control the display of other fields on the digestate/energy pages are modified,
// a modal is displayed after form submission to inform the user that there are new fields to fill out on those pages.
// This occurs when watched fields (such as tariff_reference or installation_category) change, which may reveal
// or hide additional fields in the digestate and energy declaration forms.
export const WatchedFieldsChanged: Story = {
  args: {
    contract: {
      ...contractData,
      pap_contracted: 10,
    },
  },
  decorators: [
    generateWatchedFieldsProvider([
      "tariff_reference",
      "installation_category",
    ]),
  ],
  play: async ({ canvasElement, step }) => {
    const { getByRole, getAllByRole } = within(canvasElement)

    await step("Open the editable card", async () => {
      const editButton = await waitFor(() =>
        getByRole("button", { name: "Modifier" })
      )
      await userEvent.click(editButton)
    })

    await step("Change installation_category", async () => {
      // Couldn't found a better way to select the installation_category select
      const selectInstallationCategory = await waitFor(
        () => getAllByRole("combobox")[1]
      )

      if (!selectInstallationCategory)
        throw new Error("Select installation_category not found")

      await fireEvent.change(selectInstallationCategory, {
        target: { value: InstallationCategory.INSTALLATION_CATEGORY_3 },
      })
    })

    await step("Submit the form", async () => {
      const submitButton = await waitFor(() =>
        getByRole("button", { name: "Sauvegarder" })
      )
      await userEvent.click(submitButton)
    })
  },
}
