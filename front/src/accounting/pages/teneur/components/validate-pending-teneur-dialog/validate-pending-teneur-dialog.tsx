import { Dialog } from "common/components/dialog2"
import { Table } from "common/components/table2"
import { useTranslation } from "react-i18next"
import {
  getBalancesBySector,
  getElecBalance,
  validateTeneurBiofuel,
  validateTeneurElec,
} from "../../api"
import { useMutation, useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useValidatePendingTeneurDialog } from "./validate-pending-teneur-dialog.hooks"
import { NoResult } from "common/components/no-result2"
import { Text } from "common/components/text"
import { useUnit } from "common/hooks/unit"
import { ExtendedUnit } from "common/types"
import { Button } from "common/components/button2"
import { useNotify } from "common/components/notifications"

export const ValidatePendingTeneurDialog = ({
  onClose,
}: {
  onClose: () => void
}) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const columns = useValidatePendingTeneurDialog()
  const { unitLabel } = useUnit(ExtendedUnit.GJ)

  const biofuel = useQuery(getBalancesBySector, {
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

  const validateTeneur = (entity_id: number) => {
    // only call an endpoint if there is some teneur linked to it
    return Promise.all([
      biofuelResults.some((b) => b.pending_teneur > 0) &&
        validateTeneurBiofuel(entity_id),
      elecResults.some((b) => b.pending_teneur > 0) &&
        validateTeneurElec(entity_id),
    ])
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

  return (
    <Dialog
      onClose={onClose}
      header={<Dialog.Title>{t("Valider ma teneur")}</Dialog.Title>}
      footer={
        <Button
          onClick={() => mutation.execute(entity.id)}
          loading={mutation.loading}
        >
          {t("Valider ma teneur")}
        </Button>
      }
      fullWidth
    >
      {!loading && results && results?.length === 0 ? (
        <NoResult />
      ) : (
        <>
          <Text fontWeight="bold" size="sm">
            <sup>*</sup>
            {`${t("Toutes les quantités sont exprimées en")} ${unitLabel}`}
          </Text>
          <Table columns={columns} rows={results} loading={loading} />
        </>
      )}
    </Dialog>
  )
}
