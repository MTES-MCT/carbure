import { Dialog } from "common/components/dialog2"
import { Table } from "common/components/table2"
import { useTranslation } from "react-i18next"
import { getBalancesBySector } from "../../api"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useValidatePendingTeneurDialog } from "./validate-pending-teneur-dialog.hooks"
import { NoResult } from "common/components/no-result2"
import { Text } from "common/components/text"
import { useUnit } from "common/hooks/unit"
import { ExtendedUnit } from "common/types"
export const ValidatePendingTeneurDialog = ({
  onClose,
}: {
  onClose: () => void
}) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const columns = useValidatePendingTeneurDialog()
  const { unitLabel } = useUnit(ExtendedUnit.GJ)
  const { result, loading } = useQuery(getBalancesBySector, {
    key: "balances-by-sector",
    params: [entity.id],
  })

  return (
    <Dialog
      onClose={onClose}
      header={
        <Dialog.Title>
          {t("Valider ma teneur mensuelle") + "- Mars 2025"}
        </Dialog.Title>
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
