import type { Meta, StoryObj } from "@storybook/react"
import { AnnualDeclarationStoryUtils } from "biomethane/providers/annual-declaration/annual-declaration.stories.utils"
import { ContractInfos } from "./contract-infos"
import { contractData } from "../../tests/contract.data"
import { generateWatchedFieldsProvider } from "biomethane/providers/watched-fields/watched-fields.stories.utils"
import { updateContractOk } from "../../tests/api"
import { okEntitySearch } from "common/__test__/api"
import GLOBAL_MOCKS from "@storybook/mocks"
import { InstallationCategory, TariffReference } from "../../types"
import { fireEvent, userEvent, waitFor, within } from "@storybook/test"
import { mockUser } from "common/__test__/helpers"
import { EntityType } from "common/types"
import { producer } from "common/__test__/data"

const MOCKS = [
  ...GLOBAL_MOCKS,
  ...AnnualDeclarationStoryUtils.parameters.msw.handlers,
  updateContractOk,
  okEntitySearch,
]
const meta: Meta<typeof ContractInfos> = {
  title: "modules/biomethane/pages/contract/components/ContractInfos",
  component: ContractInfos,
  ...AnnualDeclarationStoryUtils,
  parameters: {
    msw: {
      handlers: MOCKS,
    },
  },
  decorators: [
    ...AnnualDeclarationStoryUtils.decorators,
    generateWatchedFieldsProvider([]),
  ],
}

export default meta

type Story = StoryObj<typeof ContractInfos>

export const WithCMAX: Story = {
  parameters: {
    docs: {
      description:
        "When the tariff reference is 2011 or 2020, CMAX field is displayed",
    },
  },
  args: {
    contract: {
      ...contractData,
      tariff_reference: TariffReference.Value2011,
    },
  },
}

export const CMAXHigherThanThreshold: Story = {
  parameters: {
    docs: {
      description:
        "When the CMAX is higher than the threshold, the RED II notice is displayed",
    },
  },
  args: {
    contract: {
      ...contractData,
      tariff_reference: TariffReference.Value2011,
      cmax: 1000,
    },
  },
}

export const WithPAP: Story = {
  parameters: {
    docs: {
      description:
        "When the tariff reference is 2021 or 2023, PAP field is displayed",
    },
  },
  args: {
    contract: contractData,
  },
}

export const PAPHigherThanThreshold: Story = {
  parameters: {
    docs: {
      description:
        "When the PAP is higher than the threshold, the RED II notice is displayed",
    },
  },
  args: {
    contract: {
      ...contractData,
      pap_contracted: 1000,
    },
  },
}

export const WatchedFieldsChanged: Story = {
  parameters: {
    docs: {
      description:
        "When certain fields that conditionally control the display of other fields on the digestate/energy pages are modified, a modal is displayed after form submission to inform the user that there are new fields to fill out on those pages. This occurs when watched fields (such as tariff_reference or installation_category) change, which may reveal or hide additional fields in the digestate and energy declaration forms.",
    },
  },
  args: {
    contract: {
      ...contractData,
      pap_contracted: 10,
      buyer: undefined,
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

    await step("Change buyer", async () => {
      const buyerAutocomplete = await waitFor(() => getByRole("textbox"))
      await userEvent.click(buyerAutocomplete)

      await userEvent.type(buyerAutocomplete, producer.name)
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

export const WatchedFieldsModalIsNotDisplayed: Story = {
  ...WatchedFieldsChanged,
  parameters: {
    docs: {
      description:
        "If the user change a field that is not watched, the modal is not displayed",
    },
  },

  decorators: [generateWatchedFieldsProvider(["tariff_reference"])],
}

export const ChooseRedIIEligibilityWithCMAXLowerThanThreshold: Story = {
  parameters: {
    docs: {
      description:
        "If the current entity is RED II, and the cmax is lower than the threshold, the RED II eligibility modal is displayed",
    },
    msw: {
      handlers: [
        mockUser(EntityType.Producteur_de_biom_thane, {
          right: {
            entity: {
              is_red_ii: true,
            },
          },
        }),
        MOCKS,
      ],
    },
  },
  args: {
    contract: {
      ...contractData,
      tariff_reference: TariffReference.Value2011,
      cmax_annualized: false,
    },
  },
  play: async ({ canvasElement, step }) => {
    const { getByRole } = within(canvasElement)

    await step("Open the editable card", async () => {
      const editButton = await waitFor(() =>
        getByRole("button", { name: "Modifier" })
      )
      await userEvent.click(editButton)
    })

    await step("Change cmax or pap", async () => {
      const numberInput = await waitFor(() => getByRole("spinbutton"))
      await userEvent.type(numberInput, "10")
    })

    await step("Submit the form", async () => {
      const submitButton = await waitFor(() =>
        getByRole("button", { name: "Sauvegarder" })
      )
      await userEvent.click(submitButton)
    })
  },
}

export const ChooseRedIIEligibilityWithPAPLowerThanThreshold: Story = {
  ...ChooseRedIIEligibilityWithCMAXLowerThanThreshold,
  parameters: {
    ...ChooseRedIIEligibilityWithCMAXLowerThanThreshold.parameters,
    docs: {
      description:
        "If the current entity is RED II, and the pap is lower than the threshold, the RED II eligibility modal is displayed",
    },
  },

  args: {
    contract: contractData,
  },
}
