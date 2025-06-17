import { useTranslation } from "react-i18next"
import {
  TransferCertificate,
  TransferCertificateFilter,
  TransferCertificateOrder,
  TransferCertificateStatus,
} from "../../types"
import { formatDate, formatNumber } from "common/utils/formatters"
import { Column } from "common/components/table2"
import { Tab } from "common/components/tabs2"
import useEntity from "common/hooks/entity"
import { compact } from "common/utils/collection"
import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "common/hooks/query-builder-2"
import { useParams } from "react-router-dom"

export function useStatus() {
  const params = useParams<"status">()
  return (params.status ?? "pending") as TransferCertificateStatus
}

export function useController(year: number, status: TransferCertificateStatus) {
  const entity = useEntity()

  const [state, actions] = useCBQueryParamsStore<
    TransferCertificateStatus,
    undefined
  >(entity, year, status)

  const query = useCBQueryBuilder<
    TransferCertificateOrder[],
    TransferCertificateStatus,
    undefined
  >(state)

  return { state, actions, query }
}

export function useTabs(): Tab<string>[] {
  const { t } = useTranslation()
  return [
    {
      key: "pending",
      label: t("En attente"),
      icon: "fr-icon-time-line",
      iconActive: "fr-icon-time-fill",
      path: "../transfer/pending",
    },
    {
      key: "accepted",
      label: t("Accepté"),
      icon: "fr-icon-success-line",
      iconActive: "fr-icon-success-fill",
      path: "../transfer/accepted",
    },
    {
      key: "rejected",
      label: t("Refusé"),
      icon: "fr-icon-error-line",
      iconActive: "fr-icon-error-fill",
      path: "../transfer/rejected",
    },
  ]
}

export function useFilters() {
  const { t } = useTranslation()
  const entity = useEntity()

  const filters: Record<string, string> = {
    [TransferCertificateFilter.Cpo]: t("Aménageur"),
    [TransferCertificateFilter.Operator]: t("Redevable"),
  }

  if (entity.isCPO) {
    delete filters[TransferCertificateFilter.Cpo]
  }

  return filters
}

export function useColumns() {
  const { t } = useTranslation()
  const entity = useEntity()

  return compact([
    {
      key: "transfer_date",
      header: t("Date de cession"),
      cell: (p) => formatDate(p.transfer_date),
    },
    (entity.isAdmin || entity.isExternal) && {
      key: "cpo",
      header: t("Aménageur"),
      cell: (p) => p.supplier.name,
    },
    {
      key: "operator",
      header: t("Redevable"),
      cell: (p) => p.client.name,
    },
    {
      key: "energy_amount",
      header: t("Quantité transférée (MWh)"),
      cell: (p) => `${formatNumber(p.energy_amount)}`,
    },
  ]) satisfies Column<TransferCertificate>[]
}
