import { Dialog } from "common/components/dialog2"
import { useTranslation } from "react-i18next"
import {
  getBiofuelBalance,
  getElecBalance,
  validateTeneurBiofuel,
  validateTeneurElec,
} from "../../api"
import { useMutation, useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import {
  useBiofuelTeneurColumns,
  useElecTeneurColumns,
} from "./validate-pending-teneur-dialog.hooks"
import { NoResult } from "common/components/no-result2"
import { Button } from "common/components/button2"
import { useNotify } from "common/components/notifications"
import { Tabs } from "common/components/tabs2"
import { compact } from "common/utils/collection"
import { SectorTabs } from "accounting/types"
import { useState } from "react"
import { Table } from "common/components/table2"

export const ValidatePendingTeneurDialog = ({
  onClose,
}: {
  onClose: () => void
}) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()

  const biofuelColumns = useBiofuelTeneurColumns()
  const elecColumns = useElecTeneurColumns()

  const [tab, setTab] = useState<string>(SectorTabs.BIOFUELS)

  const biofuel = useQuery(getBiofuelBalance, {
    key: "balances-by-sector",
    params: [entity.id],
  })

  const elec = useQuery(getElecBalance, {
    key: "elec-balance",
    params: [entity.id],
  })

  const loading = biofuel.loading || elec.loading

  const biofuelsRes = biofuel.result?.data.results ?? []
  const elecRes = elec.result?.data?.results ?? []

  const results = [...biofuelsRes, ...elecRes]

  const pendingBiofuels = biofuelsRes.filter((r) => r.pending_teneur > 0).length
  const pendingElec = elecRes.filter((r) => r.pending_teneur > 0).length

  const validateTeneur = async (entity_id: number) => {
    if (pendingBiofuels > 0) {
      await validateTeneurBiofuel(entity_id)
    }

    if (pendingElec > 0) {
      await validateTeneurElec(entity_id)
    }
  }

  const mutation = useMutation(validateTeneur, {
    onSuccess: () => {
      onClose()
      notify(
        t("Les opérations de teneur en attente ont été validées avec succès."),
        { variant: "success" }
      )
    },
    onError: () => {
      notify(
        t(
          "Une erreur est survenue lors de la validation des opérations de teneur en attente."
        ),
        { variant: "danger" }
      )
    },
  })

  const biofuelPendingMark = pendingBiofuels > 0 ? ` (${pendingBiofuels})` : ""
  const elecPendingMark = pendingElec > 0 ? ` (${pendingElec})` : ""

  return (
    <Dialog
      onClose={onClose}
      header={<Dialog.Title>{t("Valider ma teneur")}</Dialog.Title>}
      footer={
        <Button
          disabled={pendingBiofuels === 0 && pendingElec === 0}
          onClick={() => mutation.execute(entity.id)}
          loading={mutation.loading}
        >
          {t("Valider ma teneur")}
        </Button>
      }
      fullWidth
    >
      <Tabs
        focus={tab}
        onFocus={setTab}
        tabs={compact([
          {
            key: SectorTabs.BIOFUELS,
            label: t("Biocarburants"),
            icon: "fr-icon-gas-station-fill",
          },
          entity.has_elec && {
            key: SectorTabs.ELEC,
            label: t("Électricité"),
            icon: "fr-icon-charging-pile-2-fill",
          },
        ])}
      />

      {!loading && results && results?.length === 0 ? (
        <NoResult />
      ) : (
        <>
          {tab === SectorTabs.BIOFUELS && (
            <Table
              loading={loading}
              columns={biofuelColumns}
              rows={biofuelsRes}
            />
          )}
          {tab === SectorTabs.ELEC && (
            <Table //
              loading={loading}
              columns={elecColumns}
              rows={elecRes}
            />
          )}
        </>
      )}
    </Dialog>
  )
}
