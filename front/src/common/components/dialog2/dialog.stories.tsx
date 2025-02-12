import type { Meta, StoryObj } from "@storybook/react"
import { Confirm, Dialog } from "./dialog"
import { Button } from "../button2"

const meta: Meta<typeof Dialog> = {
  component: Dialog,
  title: "common/components/Dialog",
  args: {
    header: (
      <>
        <Dialog.Title>Ajout organisation</Dialog.Title>
        <Dialog.Description>
          Ajouter une organisation à votre compte
        </Dialog.Description>
      </>
    ),
    children: <>une section</>,
    footer: (
      <>
        <Button>Valider</Button>
        <Button priority="secondary">Refuser</Button>
      </>
    ),
  },
}

type Story = StoryObj<typeof Dialog>

export default meta

export const Default: Story = {}

export const ConfirmDialog: StoryObj<typeof Confirm> = {
  args: {
    confirm: "Valider",
    description: "avec une description",
    title: "Titre de la dialog",
  },
  render: (args) => <Confirm {...args} />,
}

export const FullWidth: Story = {
  args: {
    fullWidth: true,
  },
}

export const FullHeight: Story = {
  args: {
    fullHeight: true,
  },
}
