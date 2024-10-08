import type { Meta, StoryObj } from "@storybook/react"

import { Button } from "./button"
import { Cross } from "./icons"
import { Button as ButtonDSFR } from "@codegouvfr/react-dsfr/Button"

const meta: Meta<typeof Button> = {
  component: Button,
  args: {
    variant: "primary",
    label: "Button",
  },
  title: "ui/button",
  parameters: {
    chromatic: { disableSnapshot: true },
  },
}
type Story = StoryObj<typeof Button>

export default meta

export const AllVariants: Story = {
  args: {
    label: "Button",
  },
  render: (args) => {
    return (
      <>
        <h1>Buttons</h1>
        <div
          style={{
            display: "flex",
            gap: "8px",
            width: "fit-content",
            flexWrap: "wrap",
            marginBottom: "8px",
            alignItems: "flex-end",
          }}
        >
          <Button {...args} label="Primary" />
          <Button {...args} variant="secondary" label="Secondary" />
          <Button {...args} variant="danger" label="Danger" />
          <Button {...args} variant="success" label="Success" />
          <Button {...args} variant="text" label="Simple text" />
          <Button {...args} variant="warning" label="Warning" />
          <Button {...args} variant="link" label="With link" />
          <Button {...args} variant="primary" label="Disabled" disabled />
          <Button {...args} variant="primary" label="Loading" loading />
          <Button {...args} variant="icon" icon={Cross} />
        </div>
        <h1>Buttons DSFR</h1>
        <div
          style={{
            display: "flex",
            gap: "8px",
            width: "fit-content",
            flexWrap: "wrap",
            alignItems: "flex-end",
          }}
        >
          <ButtonDSFR priority="primary">Primary</ButtonDSFR>
          <ButtonDSFR priority="secondary">Secondary</ButtonDSFR>
          <ButtonDSFR priority="tertiary">Tertiary</ButtonDSFR>
          <ButtonDSFR priority="tertiary no outline">
            Tertiary no outline
          </ButtonDSFR>
          <ButtonDSFR priority="primary" iconId="fr-icon-checkbox-circle-line">
            With icon DSFR
          </ButtonDSFR>
          <ButtonDSFR
            linkProps={{
              href: "#",
            }}
          >
            With link
          </ButtonDSFR>
          <ButtonDSFR
            iconId="fr-icon-checkbox-circle-line"
            priority="tertiary no outline"
            title="Label button"
          />
          <ButtonDSFR title="Label button" size="small">
            Small with our icon
            <Cross />
          </ButtonDSFR>
          <ButtonDSFR title="Label button" size="medium">
            Medium
            <Cross />
          </ButtonDSFR>
          <ButtonDSFR title="Label button" size="large">
            Large
            <Cross />
          </ButtonDSFR>
        </div>
        <h1 style={{ marginTop: "40px" }}>Commentaires</h1>
        <ul>
          <li>
            Si on utilise pas la librairie d'icones du DSFR, on va devoir
            bricoler un peu pour avoir le même affichage.
          </li>
          <li>
            En première étape de migration DSFR, on avait parlé de migrer les
            boutons. Si on utilise la librairie d'icones du DSFR, il va falloir
            aussi remplacer toutes les icones du projet par leur équivalent (si
            il existe)
          </li>
        </ul>
      </>
    )
  },
}
