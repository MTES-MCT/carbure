import { Button } from "common/components/button2"
import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { findFossilFuels } from "common/api"
import { apiTypes } from "common/services/api-fetch.types"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { MultiSelect } from "common/components/selects2/multiselect"
import { Notice } from "common/components/notice"

type MacFuelSelectionDialogProps = {
  existingFuels: string[]
  onAdd: (fuels: string[]) => void
  onClose: () => void
}

type FossilFuel = apiTypes["FossilFuel"]

export const MacFuelSelectionDialog = ({
  existingFuels,
  onAdd,
  onClose,
}: MacFuelSelectionDialogProps) => {
  const { t } = useTranslation()
  const [selectedFuels, setSelectedFuels] = useState<string[]>([])

  const getOptions = async () =>
    (await findFossilFuels()).filter(
      (fuel) => !existingFuels.includes(fuel.nomenclature)
    )

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
          clear
          placeholder={t("Choisissez des carburants")}
          value={selectedFuels}
          getOptions={getOptions}
          onChange={(fuels) => setSelectedFuels(fuels ?? [])}
          normalize={(fuel) => ({
            value: fuel.nomenclature,
            label: fuel.label,
          })}
        />
      </Dialog>
    </Portal>
  )
}
