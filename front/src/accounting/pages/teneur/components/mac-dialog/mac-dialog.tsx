import { Button } from "common/components/button2"
import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { usePortal } from "common/components/portal"
import { Table } from "common/components/table2"
import { useTranslation } from "react-i18next"
import css from "./mac-dialog.module.css"
import { findFossilFuels } from "common/api"
import { useMutation, useQuery } from "common/hooks/async"
import { getMacFossilFuels, replaceMacFossilFuels } from "../../api"
import { MacFuelSelectionDialog } from "./mac-fuel-selection-dialog"
import { useMacDialogDraft, useMacTable } from "./mac-dialog.hooks"
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

  const { result: fossilFuels = [], loading: fossilFuelsLoading } = useQuery(
    findFossilFuels,
    {
      key: "fossil-fuels",
      params: [],
    }
  )

  const { macData, fuels, setMacData, addFuels, clearDraft, hasLocalDraft } =
    useMacDialogDraft(entityId, year, loadedMacData, readOnly)

  const mutation = useMutation(replaceMacFossilFuels, {
    invalidates: ["mac-fossil-fuels", "teneur-objectives"],
    onSuccess: clearDraft,
  })

  const selectableFossilFuels = fossilFuels.filter(
    (fuel) => !fuels.includes(fuel.nomenclature)
  )

  const table = useMacTable(
    year,
    macData,
    fuels,
    fossilFuels,
    setMacData,
    readOnly
  )

  const openFuelSelectionDialog = () => {
    portal((close) => (
      <MacFuelSelectionDialog
        fossilFuels={selectableFossilFuels}
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
              {hasLocalDraft && (
                <Notice
                  icon="fr-icon-warning-line"
                  className={css.notice}
                  variant="warning"
                >
                  {t("Les valeurs affichées ne sont pas encore enregistrées.")}
                </Notice>
              )}
              <Button
                priority="primary"
                onClick={saveMacData}
                disabled={!hasLocalDraft}
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
            loading={loading || fossilFuelsLoading}
          />
        )}
      </Dialog>
    </Portal>
  )
}
