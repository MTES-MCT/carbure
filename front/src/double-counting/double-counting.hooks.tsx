import { useQuery } from "common/hooks/async"
import { getDoubleCountingAgreements } from "./api"
import useEntity from "common/hooks/entity"
import { useMemo, useState } from "react"
import { isAgreementExpired } from "./utils"
import { DoubleCountingStatus } from "./types"
import { apiTypes } from "common/services/api-fetch.types"
import { Column, Cell } from "common/components/table2"
import { useTranslation } from "react-i18next"
import ApplicationStatus from "./components/application-status"
import { formatDate, formatDateYear } from "common/utils/formatters"

export enum DoubleCountingTab {
  ACTIVE = "active",
  PENDING = "pending",
  REJECTED_OR_EXPIRED = "rejected_or_expired",
}

export const useDoubleCounting = () => {
  const [tab, setTab] = useState<DoubleCountingTab>(DoubleCountingTab.ACTIVE)
  const entity = useEntity()
  const { result, loading } = useQuery(getDoubleCountingAgreements, {
    key: "dc-agreements",
    params: [entity.id],
  })

  const applicationsByStatus = useMemo(() => {
    const data = result?.data ?? []
    return Object.groupBy(data, ({ status, period_end }) => {
      if (
        isAgreementExpired(period_end) ||
        status === DoubleCountingStatus.REJECTED
      ) {
        return DoubleCountingTab.REJECTED_OR_EXPIRED
      } else if (status === DoubleCountingStatus.PENDING) {
        return DoubleCountingTab.PENDING
      }
      return DoubleCountingTab.ACTIVE
    })
  }, [result?.data])

  return {
    tab,
    setTab,
    loading,
    applications: applicationsByStatus[tab] ?? [],
  }
}

export const useDoubleCountingColumns = () => {
  const { t } = useTranslation()
  const columns: Column<apiTypes["DoubleCountingApplicationPartial"]>[] = [
    {
      header: t("Statut"),
      cell: (dc) => (
        <ApplicationStatus status={dc.status} expirationDate={dc.period_end} />
      ),
    },
    {
      header: t("Site de production"),
      cell: (dc) => <Cell text={dc.production_site.name} />,
    },
    {
      header: t("Période de validité"),
      cell: (dc) => (
        <Cell
          text={`${formatDateYear(dc.period_start)} - ${formatDateYear(dc.period_end)}`} // prettier-ignore
        />
      ),
    },
    {
      header: t("N° d'agrément"),
      cell: (dc) => (
        <span>
          {dc.status === DoubleCountingStatus.REJECTED && <>-</>}
          {dc.status === DoubleCountingStatus.PENDING &&
            t("En cours de traitement...")}

          {dc.status === DoubleCountingStatus.ACCEPTED && (
            <>{dc.certificate_id}</>
          )}
        </span>
      ),
    },
    {
      header: t("Quotas"),
      cell: (dc) => (
        <Cell
          text={
            dc.quotas_progression != null
              ? Math.round(dc.quotas_progression * 100) + "%"
              : "-"
          }
        />
      ),
    },
    {
      header: t("Date de soumission"),
      cell: (dc) => <Cell text={formatDate(dc.created_at)} />,
    },
  ]

  return columns
}
