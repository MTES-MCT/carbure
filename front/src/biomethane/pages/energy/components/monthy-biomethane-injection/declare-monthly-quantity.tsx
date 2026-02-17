import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { Form } from "common/components/form2"
import { Table } from "common/components/table2"
import { useMutation } from "common/hooks/async"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import useEntity from "common/hooks/entity"
import { saveMonthlyReports } from "../../api"
import {
  BiomethaneEnergyMonthlyReport,
  BiomethaneEnergyMonthlyReportDataRequest,
} from "../../types"
import { useDeclareMonthlyQuantityColumns } from "./declare-monthly-quantity.hooks"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useNavigate } from "react-router-dom"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"

type BiomethaneEnergyMonthlyReportForm = Partial<
  Exclude<BiomethaneEnergyMonthlyReportDataRequest, "month">
> & {
  month: number
}

interface DeclareMonthlyQuantityProps {
  isReadOnly?: boolean
  monthlyReports: BiomethaneEnergyMonthlyReport[]
}

const DEFAULT_DATA: BiomethaneEnergyMonthlyReportForm[] = Array.from(
  { length: 12 },
  (_, index) => ({
    month: index + 1, // Numéro du mois (1 à 12)
    injected_volume_nm3: 0,
    average_monthly_flow_nm3_per_hour: 0,
  })
)

export const DeclareMonthlyQuantity = ({
  isReadOnly,
  monthlyReports,
}: DeclareMonthlyQuantityProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const navigate = useNavigate()
  const { selectedYear } = useAnnualDeclaration()
  // État pour stocker toutes les valeurs du tableau
  const [tableData, setTableData] = useState<
    BiomethaneEnergyMonthlyReportForm[]
  >(monthlyReports.length > 0 ? monthlyReports : DEFAULT_DATA)

  const {
    execute: saveMonthlyReportsMutation,
    loading: saveMonthlyReportsLoading,
  } = useMutation(saveMonthlyReports, {
    invalidates: ["energy"],
    onSuccess: () => {
      notify(t("Les données ont bien été mises à jour."), {
        variant: "success",
      })
      goToEnergyPage()
    },
    onError: () => notifyError(),
  })

  const handleSubmit = () => {
    const data = tableData.map((item) => ({
      month: item.month,
      injected_volume_nm3: item.injected_volume_nm3 ?? 0,
      average_monthly_flow_nm3_per_hour:
        item.average_monthly_flow_nm3_per_hour ?? 0,
    }))
    saveMonthlyReportsMutation(entity.id, selectedYear, data)
  }

  // Fonction pour mettre à jour une valeur spécifique
  const updateCellValue = (
    month: number,
    field: keyof BiomethaneEnergyMonthlyReportForm,
    value: number | undefined
  ) => {
    setTableData((prev) =>
      prev.map((item) =>
        item.month === month ? { ...item, [field]: value } : item
      )
    )
  }

  const columns = useDeclareMonthlyQuantityColumns({
    isReadOnly: isReadOnly ?? false,
    updateCellValue,
  })

  const goToEnergyPage = () => navigate({ hash: "" })

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
            loading={saveMonthlyReportsLoading}
          >
            {t("Enregistrer")}
          </Button>
        )
      }
      onClose={goToEnergyPage}
      style={{
        width: "1000px",
      }}
    >
      <Form id="declare-monthly-quantity-form" onSubmit={handleSubmit}>
        <Table columns={columns} rows={tableData} />
      </Form>
    </Dialog>
  )
}
