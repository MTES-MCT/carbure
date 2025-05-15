import { Dialog } from "common/components/dialog2"
import { Table } from "common/components/table2"
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
import { BiofuelFill, ElecFill } from "common/components/icon"
import { useState } from "react"

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

  const biofuelResults = biofuel.result?.data.results ?? []
  const elecResults = elec.result?.data?.results ?? []

  const results = [...biofuelResults, ...elecResults]

  const validateTeneur = async (entity_id: number) => {
    if (tab === SectorTabs.BIOFUELS) {
      await validateTeneurBiofuel(entity_id)
    } else if (tab === SectorTabs.ELEC) {
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

  const hasPendingBiofuels = biofuelResults.some((r) => r.pending_teneur > 0)
  const hasPendingElec = elecResults.some((r) => r.pending_teneur > 0)

  const shouldDisable =
    (tab === SectorTabs.BIOFUELS && !hasPendingBiofuels) ||
    (tab === SectorTabs.ELEC && !hasPendingElec)

  return (
    <Dialog
      onClose={onClose}
      header={<Dialog.Title>{t("Valider ma teneur")}</Dialog.Title>}
      footer={
        <Button
          disabled={shouldDisable}
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
            icon: BiofuelFill,
          },
          entity.has_elec && {
            key: SectorTabs.ELEC,
            label: t("Électricité"),
            icon: ElecFill,
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
              rows={biofuelResults}
            />
          )}
          {tab === SectorTabs.ELEC && (
            <Table //
              loading={loading}
              columns={elecColumns}
              rows={elecResults}
            />
          )}
        </>
      )}
    </Dialog>
  )
}
