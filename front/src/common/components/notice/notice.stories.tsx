import type { Meta, StoryObj } from "@storybook/react"
import { Notice } from "./notice"
import { SurveyFill } from "../icon"

const meta: Meta<typeof Notice> = {
  component: Notice,
  title: "common/components/Notice",
  args: {
    title: "Titre principal",
    children: "Description de l'alerte",
  },
}

type Story = StoryObj<typeof Notice>

export default meta

export const Default: Story = {
  args: {
    variant: "info",
  },
}

export const Warning: Story = {
  args: {
    variant: "warning",
  },
}
export const Alert: Story = {
  args: {
    variant: "alert",
  },
}

export const Link: Story = {
  args: {
    variant: "info",
    linkText: "Lien de consultation",
    linkHref: "#",
  },
}

export const Action: Story = {
  args: {
    variant: "info",
    linkText: "Lien de consultation",
    onAction: () => {},
  },
}

export const Closable: Story = {
  args: {
    variant: "info",
    isClosable: true,
  },
}

export const WithIcon: Story = {
  args: {
    variant: "info",
    icon: SurveyFill,
  },
}
