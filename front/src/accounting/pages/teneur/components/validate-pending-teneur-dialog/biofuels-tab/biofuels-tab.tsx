import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useUnit } from "common/hooks/unit"
import { ExtendedUnit } from "common/types"
import { useBiofuelsTab } from "./biofuels-tabs.hooks"
import { NoResult } from "common/components/no-result2"
import { Text } from "common/components/text"
import { Table } from "common/components/table2"
import { useTranslation } from "react-i18next"
import { getBalances } from "accounting/api/balances"
import { OperationOrder } from "accounting/types"
export const BiofuelsTab = () => {
  const entity = useEntity()
  const { t } = useTranslation()
  const { result, loading } = useQuery(
    (entityId) =>
      getBalances({
        entity_id: entityId,
        order_by: [OperationOrder.sector],
      }),
    {
      key: "balances-by-sector",
      params: [entity.id],
    }
  )
  const columns = useBiofuelsTab()
  const { unitLabel } = useUnit(ExtendedUnit.GJ)

  return (
    <>
      {!loading &&
      result?.data?.results &&
      result?.data?.results?.length === 0 ? (
        <NoResult />
      ) : (
        <>
          <Text fontWeight="bold" size="sm">
            <sup>*</sup>
            {`${t("Toutes les quantités sont exprimées en")} ${unitLabel}`}
          </Text>
          <Table
            columns={columns}
            rows={result?.data?.results ?? []}
            loading={loading}
          />
        </>
      )}
    </>
  )
}
