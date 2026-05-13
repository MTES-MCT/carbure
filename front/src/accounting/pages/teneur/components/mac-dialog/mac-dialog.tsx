import { Button } from "common/components/button2"
import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { usePortal } from "common/components/portal"
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
import { MacFuelSelectionDialog } from "./mac-fuel-selection-dialog"
import { useMacTable } from "./mac-dialog.hooks"
import { Notice } from "common/components/notice"

type MacDialogProps = {
  onClose: () => void
  readOnly?: boolean
  entityId: number
  year: number
}

export const MacDialog = ({
  onClose,
  readOnly,
  entityId,
  year,
}: MacDialogProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  const { result: loadedMacData, loading } = useQuery(getMacFossilFuels, {
    key: "mac-fossil-fuels",
    params: [entityId, year],
  })

  const mutation = useMutation(replaceMacFossilFuels, {
    invalidates: ["mac-fossil-fuels", "teneur-objectives"],
  })

  const [macData, setMacData] = useState<MacFossilFuel[]>([])
  const [fuels, setFuels] = useState<string[]>([])

  useEffect(() => {
    if (loadedMacData) {
      setMacData(loadedMacData)
      setFuels(Array.from(new Set(loadedMacData.map((mac) => mac.fuel))))
    }
  }, [loadedMacData])

  const table = useMacTable(year, macData, fuels, setMacData, readOnly)

  const addFuels = (fuelsToAdd: string[]) => {
    setFuels((fuels) => Array.from(new Set([...fuels, ...fuelsToAdd])))
  }

  const openFuelSelectionDialog = () => {
    portal((close) => (
      <MacFuelSelectionDialog
        existingFuels={fuels}
        onAdd={(fuels) => {
          addFuels(fuels)
          close()
        }}
        onClose={close}
      />
    ))
  }

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
          !readOnly && (
            <div className={css.footer}>
              <Button
                priority="secondary"
                iconId="ri-add-fill"
                onClick={openFuelSelectionDialog}
              >
                {t("Ajouter des carburants")}
              </Button>
              <Button
                priority="primary"
                onClick={saveMacData}
                loading={mutation.loading}
              >
                {t("Sauvegarder")}
              </Button>
            </div>
          )
        }
        fullWidth
      >
        {table.columns.length <= 1 && (
          <Notice noColor variant="info">
            {t(
              "Aucune information de mise à consommation disponible pour cette année."
            )}
          </Notice>
        )}
        {table.columns.length > 1 && (
          <Table
            className={css.table}
            columns={table.columns}
            rows={table.rows}
            loading={loading}
          />
        )}
      </Dialog>
    </Portal>
  )
}
