import type { Meta, StoryObj } from "@storybook/react"

import { Placeholder } from "./icons"
import * as Icons from "./icons"

const meta: Meta<typeof Placeholder> = {
  component: Placeholder,
  title: "ui/icons",
  parameters: {
    chromatic: { disableSnapshot: true },
  },
}
type Story = StoryObj<typeof Placeholder>

export default meta

export const AllIcons: Story = {
  render: (args) => {
    return (
      <>
        <div style={{ display: "flex", gap: "20px", flexWrap: "wrap" }}>
          {Object.entries(Icons).map(([iconName, CurrentIcon]) => (
            <span
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "2px",
                alignItems: "center",
              }}
              key={iconName}
            >
              <CurrentIcon {...args} />
              <span style={{ fontSize: "12px" }}>{iconName}</span>
            </span>
          ))}
        </div>

        <h1 style={{ marginTop: "40px" }}>Commentaires</h1>
        <ul>
          <li>
            Les icones du DSFR utilisent{" "}
            <a href="https://remixicon.com/">remix icon</a>, il va falloir que
            l'on voit comment faire, car nous on utilise{" "}
            <a href="https://github.com/tabler/tabler-icons">tabler icons</a>
          </li>
        </ul>
      </>
    )
  },
}
