import { Button } from "common/components/button2"
import { usePortal } from "common/components/portal"
import { Column } from "common/components/table2"
import { useTranslation } from "react-i18next"
import { CessionDialog } from "./cession-dialog"
import useEntity from "common/hooks/entity"
import { compact } from "common/utils/collection"
import { UserRole } from "common/types"
import { formatNumber } from "common/utils/formatters"
import { ElecBalance, ElecOperationsStatus } from "accounting/types"
import { formatSector } from "accounting/utils/formatters"
import { addQueryParams } from "common/utils/routes"
import { useRoutes } from "common/hooks/routes"
import { useNavigate } from "react-router"

export const useBalancesElecColumns = () => {
  const { t } = useTranslation()
  const portal = usePortal()
  const entity = useEntity()
  const routes = useRoutes()
  const navigate = useNavigate()

  const canTransfer =
    entity.hasRights(UserRole.ReadWrite) || entity.hasRights(UserRole.Admin)

  const columns: Column<ElecBalance>[] = compact([
    {
      header: t("Filière"),
      cell: (item) => formatSector(item.sector),
    },
    {
      header: `${t("Solde disponible")} (GJ)`,
      cell: (item) =>
        formatNumber(item.available_balance / 1000, { fractionDigits: 0 }),
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
              const url = addQueryParams(routes.ACCOUNTING.OPERATIONS.ELEC, {
                status: ElecOperationsStatus.PENDING,
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
              <CessionDialog //
                balance={balance}
                onClose={close}
              />
            ))
          }
        />
      ),
    },
  ])

  return columns
}
