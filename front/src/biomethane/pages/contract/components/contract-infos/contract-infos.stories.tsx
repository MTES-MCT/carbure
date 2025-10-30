import type { Meta, StoryObj } from "@storybook/react"
import { AnnualDeclarationStoryUtils } from "biomethane/providers/annual-declaration/annual-declaration.stories.utils"
import { ContractInfos } from "./contract-infos"
import { contractData } from "../../tests/contract.data"
import { generateWatchedFieldsProvider } from "biomethane/providers/watched-fields/watched-fields.stories.utils"
import { updateContractOk } from "../../tests/api"
import { okEntitySearch } from "common/__test__/api"

const meta: Meta<typeof ContractInfos> = {
  title: "modules/biomethane/pages/contract/components/ContractInfos",
  component: ContractInfos,
  ...AnnualDeclarationStoryUtils,
  parameters: {
    msw: [
      ...AnnualDeclarationStoryUtils.parameters.msw,
      updateContractOk,
      okEntitySearch,
    ],
  },
  decorators: [
    ...AnnualDeclarationStoryUtils.decorators,
    generateWatchedFieldsProvider([]),
  ],
}

export default meta

type Story = StoryObj<typeof ContractInfos>

export const Default: Story = {
  args: {
    contract: contractData,
  },
}
