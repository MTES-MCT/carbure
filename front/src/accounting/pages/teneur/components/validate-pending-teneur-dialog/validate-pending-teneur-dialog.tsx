import { Dialog } from "common/components/dialog2"
import { Table } from "common/components/table2"
import { useTranslation } from "react-i18next"
import { getBalancesBySector, validateTeneur } from "../../api"
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
  const { result, loading } = useQuery(getBalancesBySector, {
    key: "balances-by-sector",
    params: [entity.id],
  })
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
      header={
        <Dialog.Title>
          {t("Valider ma teneur mensuelle") + " - Mars 2025"}
        </Dialog.Title>
      }
      footer={
        <Button
          onClick={() => mutation.execute(entity.id)}
          loading={mutation.loading}
        >
          {t("Valider ma teneur mensuelle")}
        </Button>
      }
      fullWidth
    >
      {!loading &&
      result?.data?.results &&
      result?.data?.results?.length === 0 ? (
        <NoResult />
      ) : (
        <>
          <Table
            columns={columns}
            rows={result?.data?.results ?? []}
            loading={loading}
          />
          <Text fontWeight="bold" size="sm">
            <sup>*</sup>
            {`${t("Toutes les quantités sont exprimées en")} ${unitLabel}`}
          </Text>
        </>
      )}
    </Dialog>
  )
}
