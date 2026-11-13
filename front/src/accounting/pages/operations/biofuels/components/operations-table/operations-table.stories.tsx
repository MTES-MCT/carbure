import type { Meta, StoryObj } from "@storybook/react"
import {
  OperationList,
  OperationsStatus,
  OperationType,
} from "accounting/types"
import { operationCredit } from "accounting/__test__/data/biofuels/operation"
import { OperationTable } from "./operations-table"

const makeIncorporationOperation = (
  overrides: Partial<OperationList> = {}
): OperationList => ({
  ...operationCredit,
  export_country: null,
  type: OperationType.INCORPORATION,
  status: OperationsStatus.DRAFT,
  renewable_energy_share: 0.5,
  volume: 1000,
  avoided_emissions: 120,
  ...overrides,
})

const meta: Meta<typeof OperationTable> = {
  component: OperationTable,
  title: "modules/accounting/pages/operations/biofuels/OperationTable",
  args: {
    rows: [makeIncorporationOperation()],
    loading: false,
  },
}

export default meta

type Story = StoryObj<typeof meta>

export const DisplaysFullPhysicalVolumeForIncorporation: Story = {}

export const GhgCorrectionsWithoutQuantityOrEmissions: Story = {
  args: {
    rows: [5, -3].map((ghg_delta, index) =>
      makeIncorporationOperation({
        id: index + 1,
        type: OperationType.CORRECTION,
        status: OperationsStatus.VALIDATED,
        volume: 0,
        quantity_renewable: 0,
        energy: 0,
        avoided_emissions: 0,
        ghg_delta,
      })
    ),
  },
}

export const CorrectedIncorporations: Story = {
  args: {
    rows: [80, 0, -25].map((corrected_avoided_emissions, index) =>
      makeIncorporationOperation({
        id: index + 1,
        status: OperationsStatus.CORRECTED,
        corrected_avoided_emissions,
      })
    ),
  },
}

export const CorrectedVolumeCorrections: Story = {
  args: {
    rows: [
      makeIncorporationOperation({
        id: 1,
        type: OperationType.CORRECTION,
        status: OperationsStatus.CORRECTED,
        corrected_avoided_emissions: 80,
      }),
      makeIncorporationOperation({
        id: 2,
        type: OperationType.CORRECTION,
        status: OperationsStatus.CORRECTED,
        transaction: "DEBIT",
        volume: -1000,
        quantity_renewable: -500,
        energy: -27000,
        avoided_emissions: 120,
        corrected_avoided_emissions: 80,
      }),
    ],
  },
}
