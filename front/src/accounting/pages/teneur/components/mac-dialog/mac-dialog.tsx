import { Button } from "common/components/button2"
import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { Table } from "common/components/table2"
import { useQuery } from "common/hooks/async"
import { useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import { getMacFossilFuels, MacFossilFuel } from "../../api"
import { useMacTable } from "./mac-dialog.hooks"
import css from "./mac-dialog.module.css"

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
  const [macData, setMacData] = useState<MacFossilFuel[]>([])

  useEffect(() => {
    if (loadedMacData) {
      setMacData(loadedMacData)
    }
  }, [loadedMacData])

  const updateVolume = (
    fuel: string,
    month: number,
    volume: number | undefined
  ) => {
    setMacData((macData) => {
      const existingMacData = macData.filter(
        (mac) =>
          !(mac.fuel === fuel && mac.year === year && mac.month === month)
      )

      if (volume === undefined) {
        return existingMacData
      }

      return [
        ...existingMacData,
        {
          fuel,
          volume,
          year,
          month,
        },
      ]
    })
  }

  const { columns, rows } = useMacTable(year, macData, updateVolume)

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
        footer={<Button onClick={onClose}>{t("Fermer")}</Button>}
        fullWidth
      >
        <Table
          className={css.table}
          columns={columns}
          rows={rows}
          loading={loading}
        />
      </Dialog>
    </Portal>
  )
}
