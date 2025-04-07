import { Button } from "common/components/button2"
import { usePortal } from "common/components/portal"
import { Column } from "common/components/table2"
import { useRoutes } from "common/hooks/routes"
import { apiTypes } from "common/services/api-fetch.types"
import { addQueryParams } from "common/utils/routes"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import { DebitOperationDialog } from "./components/debit-operation-dialog"
import {
  BalancesFilter,
  BalancesQuery,
  OperationsStatus,
} from "accounting/types"
import * as api from "accounting/api/balances"
import { formatSector } from "accounting/utils/formatters"
import { useNormalizeSector } from "accounting/hooks/normalizers"
import useEntity from "common/hooks/entity"
import { compact } from "common/utils/collection"
import { UserRole } from "common/types"
import { useUnit } from "common/hooks/unit"
import { formatNumber } from "common/utils/formatters"

export const useBalancesColumns = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const routes = useRoutes()
  const portal = usePortal()
  const entity = useEntity()
  const { unit } = useUnit()
  const canTransfer =
    entity.hasRights(UserRole.ReadWrite) || entity.hasRights(UserRole.Admin)

  const columns: Column<apiTypes["Balance"]>[] = compact([
    {
      header: t("Filière"),
      cell: (item) => t(formatSector(item.sector)),
    },
    {
      header: t("Biocarburant"),
      cell: (item) => item.biofuel?.code,
    },
    {
      header: t("Catégorie"),
      cell: (item) => item.customs_category,
    },
    {
      header: `${t("Solde disponible")} (${unit.toLocaleUpperCase()})`,
      cell: (item) =>
        formatNumber(item.available_balance, { fractionDigits: 0 }),
    },
    {
      header: t("Opérations en attente"),
      cell: (item) =>
        item.pending_operations === 0 ? (
          "-"
        ) : (
          <Button
            customPriority="link"
            onClick={() => {
              const url = addQueryParams(routes.ACCOUNTING.OPERATIONS, {
                sector: item.sector,
                biofuel: item.biofuel?.code,
                customs_category: item.customs_category,
                status: OperationsStatus.PENDING,
              })
              navigate(url)
            }}
          >
            {item.pending_operations}
          </Button>
        ),
    },
    canTransfer && {
      header: t("Céder"),
      cell: (balance) => (
        <Button
          iconId="fr-icon-send-plane-line"
          priority="tertiary"
          title={t("Céder")}
          size="small"
          onClick={() =>
            portal((close) => (
              <DebitOperationDialog onClose={close} balance={balance} />
            ))
          }
        />
      ),
    },
  ])

  return columns
}

export const useGetFilterOptions = (query: BalancesQuery) => {
  const normalizeSector = useNormalizeSector()

  const getFilterOptions = async (filter: string) => {
    const { data } = await api.getBalanceFilters(
      query,
      filter as BalancesFilter
    )

    if (!data) {
      return []
    }

    if (filter === BalancesFilter.sector) {
      return data?.map(normalizeSector)
    }

    return data
  }

  return getFilterOptions
}
