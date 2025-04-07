import { Meta, StoryObj } from "@storybook/react"
import { TicketAssignment } from "./simple-assignment"
import { safTicketSourceDetails } from "saf/__test__/data"
import { expect, fn, userEvent, waitFor, within } from "@storybook/test"
import { okFindClients, assignSafTicket } from "saf/__test__/api"

const meta = {
  title: "SAF/Components/TicketAssignment",
  component: TicketAssignment,
  parameters: {
    layout: "centered",
    msw: {
      handlers: [okFindClients, assignSafTicket],
    },
    mockingDate: new Date(2024, 3, 1), // Values for assignment_period are calculated based on this date
  },
  args: {
    ticketSource: safTicketSourceDetails,
    onClose: fn(),
    onTicketAssigned: fn(),
  },
} satisfies Meta<typeof TicketAssignment>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {}

export const NonAirlineClient: Story = {
  play: async ({ canvasElement, args, step }) => {
    const { getByPlaceholderText, getByRole } = within(canvasElement)
    const assignButton = await waitFor(() =>
      getByRole("button", { name: "Affecter" })
    )

    await step("Set volume", async () => {
      const volumeInput = await waitFor(() =>
        getByRole("button", { name: "Maximum" })
      )
      await userEvent.click(volumeInput)
    })

    await step("Select client", async () => {
      const clientInput = await waitFor(() =>
        getByPlaceholderText("Sélectionnez un client")
      )
      await userEvent.type(clientInput, "Opérateur 1")
      await userEvent.keyboard("{Enter}")
    })

    await step("Select agreement reference", async () => {
      const agreementReference = await waitFor(() =>
        getByPlaceholderText("Ex: 1234567890")
      )
      await userEvent.type(agreementReference, "11111")
    })

    await step("Assign ticket", async () => {
      await userEvent.click(assignButton)
    })

    await waitFor(() =>
      expect(args.onTicketAssigned).toHaveBeenCalledWith(
        safTicketSourceDetails.total_volume -
          safTicketSourceDetails.assigned_volume,
        "Opérateur 1"
      )
    )
  },
}
