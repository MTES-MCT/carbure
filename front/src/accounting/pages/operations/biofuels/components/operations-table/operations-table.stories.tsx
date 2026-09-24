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
): OperationList =>
  ({
    ...operationCredit,
    type: OperationType.INCORPORATION,
    status: OperationsStatus.DRAFT,
    renewable_energy_share: 0.5,
    volume: 1000,
    avoided_emissions: 120,
    ...overrides,
  }) as OperationList

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
