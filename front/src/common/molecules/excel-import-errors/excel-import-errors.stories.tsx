import type { Meta, StoryObj } from "@storybook/react"
import { ExcelImportErrors } from "./excel-import-errors"

const meta: Meta<typeof ExcelImportErrors> = {
  component: ExcelImportErrors,
  title: "common/molecules/ExcelImportErrors",
  args: {
    importErrors: {
      total_errors: 4,
      total_rows_processed: 10,
      validation_errors: [
        {
          row: 3,
          errors: {
            volume: ["Ce champ est obligatoire"],
            feedstock: ["Valeur invalide"],
          },
        },
        {
          row: 5,
          errors: {
            origin_country: ["Code pays inconnu"],
          },
        },
        {
          row: 7,
          errors: {
            average_weighted_distance_km: [
              "La distance doit être un nombre positif",
            ],
          },
        },
      ],
    },
  },
  render: (args) => {
    return (
      <div style={{ maxWidth: "800px", padding: "2rem" }}>
        <ExcelImportErrors {...args} />
      </div>
    )
  },
}

type Story = StoryObj<typeof ExcelImportErrors>

export default meta

export const Default: Story = {}

export const WithFieldLabels: Story = {
  args: {
    fieldLabels: {
      volume: "Volume (L)",
      feedstock: "Intrant",
      origin_country: "Pays d'origine",
      average_weighted_distance_km: "Distance moyenne pondérée (km)",
    },
  },
}

export const SingleError: Story = {
  args: {
    importErrors: {
      total_errors: 1,
      total_rows_processed: 50,
      validation_errors: [
        {
          row: 12,
          errors: {
            biofuel: ["Le biocarburant ETH95 n'est pas reconnu"],
          },
        },
      ],
    },
  },
}

export const ManyErrors: Story = {
  args: {
    importErrors: {
      total_errors: 8,
      total_rows_processed: 25,
      validation_errors: [
        {
          row: 2,
          errors: {
            lot_id: ["Lot introuvable"],
            volume: ["Volume insuffisant"],
          },
        },
        {
          row: 3,
          errors: {
            operation_type: ["Type d'opération invalide"],
          },
        },
        {
          row: 5,
          errors: {
            credited_entity: ["Entité destinataire inconnue"],
          },
        },
        {
          row: 8,
          errors: {
            volume: ["Volume négatif non autorisé"],
          },
        },
        {
          row: 10,
          errors: {
            lot_id: ["Format invalide"],
            volume: ["Ce champ est obligatoire"],
          },
        },
      ],
    },
  },
}
