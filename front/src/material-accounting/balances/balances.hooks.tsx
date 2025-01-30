import { Button } from "common/components/button2"
import { usePortal } from "common/components/portal"
import { Column } from "common/components/table2"
import { useRoutes } from "common/hooks/routes"
import { apiTypes } from "common/services/api-fetch.types"
import { formatNumber } from "common/utils/formatters"
import { addQueryParams } from "common/utils/routes"
import { formatSector } from "material-accounting/operations/operations.utils"
import { OperationsStatus } from "material-accounting/operations/types"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import { DebitOperationDialog } from "./components/debit-operation-dialog"

export const useBalancesColumns = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const routes = useRoutes()
  const portal = usePortal()

  const columns: Column<apiTypes["Balance"]>[] = [
    {
      header: t("Filière"),
      cell: (item) => t(formatSector(item.sector)),
    },
    {
      header: t("Biocarburant"),
      cell: (item) => item.biofuel,
    },
    {
      header: t("Catégorie"),
      cell: (item) => item.customs_category,
    },
    {
      header: t("Solde disponible"),
      cell: (item) => formatNumber(Number(item.available_balance)),
    },
    {
      header: t("Opérations en attente"),
      cell: (item) =>
        item.pending === 0 ? (
          item.pending
        ) : (
          <Button
            customPriority="link"
            onClick={() => {
              const url = addQueryParams(
                routes.MATERIAL_ACCOUNTING.OPERATIONS,
                {
                  sector: item.sector,
                  biofuel: item.biofuel,
                  customs_category: item.customs_category,
                  status: OperationsStatus.PENDING,
                }
              )
              navigate(url)
            }}
          >
            {item.pending}
          </Button>
        ),
    },
    {
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
  ]

  return columns
}
