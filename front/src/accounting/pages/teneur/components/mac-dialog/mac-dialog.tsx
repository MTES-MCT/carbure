import { Button } from "common/components/button2"
import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { Table } from "common/components/table2"
import { useTranslation } from "react-i18next"
import { useMacTable } from "./mac-dialog.hooks"
import css from "./mac-dialog.module.css"

type MacDialogProps = {
  onClose: () => void
  year: number
}

export const MacDialog = ({ onClose, year }: MacDialogProps) => {
  const { t } = useTranslation()
  const { columns, rows } = useMacTable(year)

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
        <Table className={css.table} columns={columns} rows={rows} />
      </Dialog>
    </Portal>
  )
}
