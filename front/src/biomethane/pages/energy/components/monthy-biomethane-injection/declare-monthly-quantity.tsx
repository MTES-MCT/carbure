import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { Form } from "common/components/form2"
import { NumberInput } from "common/components/inputs2"
import { Table } from "common/components/table2"
import { formatMonth } from "common/utils/formatters"
import { useState } from "react"
import { useTranslation } from "react-i18next"

interface DeclareMonthlyQuantityData {
  month: number
  injected_volume?: number
  average_flow?: number
  operating_hours?: number
}

interface DeclareMonthlyQuantityProps {
  onClose: () => void
  data: DeclareMonthlyQuantityData[]
  isReadOnly?: boolean
}

const DEFAULT_DATA: DeclareMonthlyQuantityData[] = Array.from(
  { length: 12 },
  (_, index) => ({
    month: index + 1, // Numéro du mois (1 à 12)
    injected_volume: undefined,
    average_flow: undefined,
    operating_hours: undefined,
  })
)

export const DeclareMonthlyQuantity = ({
  onClose,
  data,
  isReadOnly,
}: DeclareMonthlyQuantityProps) => {
  const { t } = useTranslation()

  // État pour stocker toutes les valeurs du tableau
  const [tableData, setTableData] = useState<DeclareMonthlyQuantityData[]>(
    data.length > 0 ? data : DEFAULT_DATA
  )

  // Fonction pour mettre à jour une valeur spécifique
  const updateCellValue = (
    month: number,
    field: keyof DeclareMonthlyQuantityData,
    value: number | undefined
  ) => {
    setTableData((prev) =>
      prev.map((item) =>
        item.month === month ? { ...item, [field]: value } : item
      )
    )
  }

  const columns: Column<DeclareMonthlyQuantityData>[] = [
    {
      header: t("Mois"),
      cell: (item) => formatMonth(item.month),
    },
    {
      header: t("Volume injecté (Nm³)"),
      cell: (item) => (
        <NumberInput
          value={item.injected_volume}
          onChange={(value) =>
            updateCellValue(item.month, "injected_volume", value)
          }
          readOnly={isReadOnly}
          required
        />
      ),
    },
    {
      header: t("Débit moyen mensuel (Nm³/h)"),
      cell: (item) => (
        <NumberInput
          value={item.average_flow}
          onChange={(value) =>
            updateCellValue(item.month, "average_flow", value)
          }
          readOnly={isReadOnly}
          required
        />
      ),
    },
    {
      header: t("Heures d'injection (h)"),
      cell: (item) => (
        <NumberInput
          value={item.operating_hours}
          onChange={(value) =>
            updateCellValue(item.month, "operating_hours", value)
          }
          readOnly={isReadOnly}
          required
        />
      ),
    },
  ]

  return (
    <Dialog
      header={
        <Dialog.Title>
          {t("Déclarer mes volumes mensuels de biométhane injecté")}
        </Dialog.Title>
      }
      footer={
        !isReadOnly && (
          <Button
            type="submit"
            nativeButtonProps={{ form: "declare-monthly-quantity-form" }}
          >
            {t("Enregistrer")}
          </Button>
        )
      }
      onClose={onClose}
      fitContent
    >
      <Form id="declare-monthly-quantity-form">
        <Table columns={columns} rows={tableData} />
      </Form>
    </Dialog>
  )
}
