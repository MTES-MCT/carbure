import { FossilFuel } from "accounting/pages/teneur/types"
import { Button } from "common/components/button2"
import Dialog from "common/components/dialog2/dialog"
import { Notice } from "common/components/notice"
import Portal from "common/components/portal"
import { MultiSelect } from "common/components/selects2"
import { useState } from "react"
import { useTranslation } from "react-i18next"

type MacFuelSelectionDialogProps = {
  fossilFuels: FossilFuel[]
  onAdd: (fuels: string[]) => void
  onClose: () => void
}

export const MacFuelSelectionDialog = ({
  fossilFuels,
  onAdd,
  onClose,
}: MacFuelSelectionDialogProps) => {
  const { t } = useTranslation()
  const [selectedFuels, setSelectedFuels] = useState<string[]>([])

  return (
    <Portal>
      <Dialog
        fitContent
        onClose={onClose}
        header={<Dialog.Title>{t("Ajouter des carburants")}</Dialog.Title>}
        footer={
          <Button
            priority="primary"
            disabled={selectedFuels.length === 0}
            onClick={() => onAdd(selectedFuels)}
          >
            {t("Ajouter")}
          </Button>
        }
        fullWidth
      >
        <Notice noColor variant="info" style={{ maxWidth: 640 }}>
          {t(
            "Veuillez choisir dans le menu ci-dessous les carburants que vous souhaitez inclure dans vos déclarations de mises à consommation. Ils s'afficheront ensuite dans le tableau, où vous pourrez en préciser les volumes."
          )}
        </Notice>

        <MultiSelect<FossilFuel, string>
          search
          placeholder={t("Choisissez des carburants")}
          value={selectedFuels}
          options={fossilFuels}
          onChange={(fuels) => setSelectedFuels(fuels ?? [])}
          normalize={(fuel) => ({
            value: fuel.nomenclature,
            label: fuel.label,
          })}
          variant="form"
        />
      </Dialog>
    </Portal>
  )
}
