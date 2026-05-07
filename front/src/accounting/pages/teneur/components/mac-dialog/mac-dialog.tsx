import { Button } from "common/components/button2"
import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { Table } from "common/components/table2"
import { useTranslation } from "react-i18next"
import css from "./mac-dialog.module.css"
import { useMutation, useQuery } from "common/hooks/async"
import {
  getMacFossilFuels,
  MacFossilFuel,
  replaceMacFossilFuels,
} from "../../api"
import { useEffect, useState } from "react"
import { useMacTable } from "./mac-dialog.hooks"

type MacDialogProps = {
  onClose: () => void
  entityId: number
  year: number
}

export const MacDialog = ({ onClose, entityId, year }: MacDialogProps) => {
  const { t } = useTranslation()

  const { result: loadedMacData, loading } = useQuery(getMacFossilFuels, {
    key: "mac-fossil-fuels",
    params: [entityId, year],
  })

  const mutation = useMutation(replaceMacFossilFuels, {
    invalidates: ["mac-fossil-fuels", "teneur-objectives"],
  })

  const [macData, setMacData] = useState<MacFossilFuel[]>([])

  useEffect(() => {
    if (loadedMacData) {
      setMacData(loadedMacData)
    }
  }, [loadedMacData])

  const table = useMacTable(year, macData, setMacData)

  const saveMacData = () => {
    mutation.execute(
      entityId,
      year,
      macData.map((mac) => ({
        fuel: mac.fuel,
        month: mac.month,
        volume: mac.volume,
      }))
    )
  }

  return (
    <Portal>
      <Dialog
        className={css.dialog}
        onClose={onClose}
        header={
          <Dialog.Title>
            {t("Renseigner mes mises à consommation") + ` (${year})`}
          </Dialog.Title>
        }
        footer={
          <Button
            priority="primary"
            onClick={saveMacData}
            loading={mutation.loading}
          >
            {t("Sauvegarder")}
          </Button>
        }
        fullWidth
      >
        <Table
          className={css.table}
          columns={table.columns}
          rows={table.rows}
          loading={loading}
        />
      </Dialog>
    </Portal>
  )
}
