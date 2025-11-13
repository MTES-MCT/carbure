import type { Meta, StoryObj } from "@storybook/react"

import { OperationDetail } from "./operation-detail"
import { generateGetOperationDetail } from "accounting/__test__/api/biofuels/operations"
import {
  operationCredit,
  operationDebit,
} from "accounting/__test__/data/biofuels/operation"
import { reactRouterParameters } from "storybook-addon-remix-react-router"
import { Operation, OperationsStatus, OperationType } from "accounting/types"
import GLOBAL_MOCKS from "@storybook/mocks"

const getOperationParameters = (
  operation: Operation,
  docDescription: string
) => ({
  docs: {
    description: docDescription,
  },
  msw: {
    handlers: [...GLOBAL_MOCKS, generateGetOperationDetail(operation)],
  },
})

const meta = {
  component: OperationDetail,
  title: "modules/accounting/pages/operations/biofuels/OperationDetail",
  parameters: {
    reactRouter: reactRouterParameters({
      location: {
        pathParams: { id: "1" },
        hash: "#operation/1",
      },
      routing: {
        path: "/operation/:id",
      },
    }),
  },
} satisfies Meta<typeof OperationDetail>

export default meta

type Story = StoryObj<typeof meta>

// TRANSFERT OPERATION

export const ReceiveTransfertOperationPending: Story = {
  name: "Transfert/Receive operation - Pending",
  parameters: getOperationParameters(
    {
      ...operationCredit,
      status: OperationsStatus.PENDING,
    },
    "Receive a transfert operation with a pending status"
  ),
}

export const ReceiveTransfertOperationAccepted: Story = {
  name: "Transfert/Receive operation - Accepted",
  parameters: getOperationParameters(
    {
      ...operationCredit,
      status: OperationsStatus.ACCEPTED,
    },
    "Receive a transfert operation with an accepted status"
  ),
}

export const SendTransfertOperationPending: Story = {
  name: "Transfert/Send operation - Pending",
  parameters: getOperationParameters(
    {
      ...operationDebit,
      status: OperationsStatus.PENDING,
    },
    "Send a transfert operation with a pending status"
  ),
}

export const SendTransfertOperationAccepted: Story = {
  name: "Transfert/Send operation - Accepted",
  parameters: getOperationParameters(
    {
      ...operationDebit,
      status: OperationsStatus.ACCEPTED,
    },
    "Send a transfert operation with an accepted status"
  ),
}

// INCORPORATION OPERATION

export const ReceiveIncorporationOperation: Story = {
  name: "Incorporation/Receive operation - Pending",
  parameters: getOperationParameters(
    {
      ...operationCredit,
      type: OperationType.INCORPORATION,
      status: OperationsStatus.PENDING,
    },
    "Receive an incorporation operation with a pending status"
  ),
}

export const ReceiveIncorporationOperationWithRenewableEnergyShare: Story = {
  name: "Incorporation/Receive operation - Pending with renewable energy share",
  parameters: getOperationParameters(
    {
      ...operationCredit,
      type: OperationType.INCORPORATION,
      status: OperationsStatus.PENDING,
      renewable_energy_share: 0.5,
    },
    "Receive an incorporation operation with a renewable energy share"
  ),
}

// EXPORTATION OPERATION

export const SendExportationOperationPending: Story = {
  name: "Exportation/Send operation - Pending",
  parameters: getOperationParameters(
    {
      ...operationDebit,
      type: OperationType.EXPORTATION,
      status: OperationsStatus.PENDING,
    },
    "Send an exportation operation with a pending status"
  ),
}

export const SendExportationOperationDraft: Story = {
  name: "Exportation/Send operation - Draft",
  parameters: getOperationParameters(
    {
      ...operationDebit,
      type: OperationType.EXPORTATION,
      status: OperationsStatus.DRAFT,
    },
    "Send an exportation operation with a draft status"
  ),
}

export const SendExpeditionOperationPending: Story = {
  name: "Expedition/Send operation - Pending",
  parameters: getOperationParameters(
    {
      ...operationDebit,
      type: OperationType.EXPEDITION,
      status: OperationsStatus.PENDING,
    },
    "Send an expedition operation with a pending status"
  ),
}

export const SendExpeditionOperationDraft: Story = {
  name: "Expedition/Send operation - Draft",
  parameters: getOperationParameters(
    {
      ...operationDebit,
      type: OperationType.EXPEDITION,
      status: OperationsStatus.DRAFT,
    },
    "Send an expedition operation with a draft status"
  ),
}

export const SendTeneurOperationPending: Story = {
  name: "Teneur/Send operation - Pending",
  parameters: getOperationParameters(
    {
      ...operationDebit,
      type: OperationType.TENEUR,
      status: OperationsStatus.PENDING,
    },
    "Send a teneur operation with a pending status"
  ),
}

export const SendTeneurOperationDeclared: Story = {
  name: "Teneur/Send operation - Declared",
  parameters: getOperationParameters(
    {
      ...operationDebit,
      type: OperationType.TENEUR,
      status: OperationsStatus.DECLARED,
    },
    "Send a teneur operation with a declared status"
  ),
}
