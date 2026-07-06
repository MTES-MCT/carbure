import { Dialog } from "common/components/dialog2"
import { useTranslation } from "react-i18next"
import { Button } from "common/components/button2"
import { Select, MultiSelect } from "common/components/selects2"
import { useState } from "react"
import { EntityPreview } from "common/types"
import useEntity from "common/hooks/entity"
import { useMutation, useQuery } from "common/hooks/async"
import { bulkTransferQualichargeVolumes, getQualichargeFilters } from "../api"
import { QualichargeFilter, QualichargeQuery } from "../types"
import { useNotify } from "common/components/notifications"
import { Text } from "common/components/text"

export type TransferVolumesDialogProps = {
  onClose: () => void
  query: QualichargeQuery
  transferTargets: EntityPreview[]
}

export const TransferVolumesDialog = ({
  onClose,
  query,
  transferTargets,
}: TransferVolumesDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()

  const [selectedOperatingUnit, setSelectedOperatingUnit] = useState<
    string[] | undefined
  >(undefined)
  const [selectedCpo, setSelectedCpo] = useState<EntityPreview | undefined>(
    undefined
  )

  const { result: operatingUnits, loading: loadingOperatingUnits } = useQuery(
    getQualichargeFilters,
    {
      key: "qualicharge-operating-units",
      params: [query, QualichargeFilter.operating_unit],
    }
  )

  const transfer = useMutation(bulkTransferQualichargeVolumes, {
    invalidates: ["qualicharge-data"],
    onSuccess: () => {
      notify(t("Les volumes ont été transférés avec succès."), {
        variant: "success",
      })
      onClose()
    },
  })

  const handleTransfer = () => {
    if (!selectedCpo || !selectedOperatingUnit) return
    transfer.execute(entity.id, selectedCpo.id, selectedOperatingUnit)
  }

  const canTransfer =
    !!selectedOperatingUnit && !!selectedCpo && !transfer.loading

  return (
    <Dialog
      header={<Dialog.Title>{t("Transférer des volumes")}</Dialog.Title>}
      footer={
        <Button
          priority="primary"
          iconId="ri-send-plane-line"
          onClick={handleTransfer}
          loading={transfer.loading}
          disabled={!canTransfer}
        >
          {t("Transférer")}
        </Button>
      }
      onClose={onClose}
    >
      <Text>
        {t(
          "Sélectionnez les unités d'exploitation pour transférer les volumes associés."
        )}
      </Text>
      <div>
        <MultiSelect
          label={t("Unités d'exploitation")}
          placeholder={t("Sélectionner une unité d'exploitation")}
          value={selectedOperatingUnit}
          options={operatingUnits ?? []}
          onChange={setSelectedOperatingUnit}
          loading={loadingOperatingUnits}
          variant="form"
        />
      </div>
      <div>
        <Select
          label={t("Destinataire")}
          placeholder={t("Sélectionner un destinataire")}
          value={selectedCpo?.id}
          options={transferTargets ?? []}
          onChange={(id) =>
            setSelectedCpo(transferTargets?.find((c) => c.id === id))
          }
          normalize={(cpo) => ({ value: cpo.id, label: cpo.name })}
          variant="form"
        />
      </div>
    </Dialog>
  )
}
