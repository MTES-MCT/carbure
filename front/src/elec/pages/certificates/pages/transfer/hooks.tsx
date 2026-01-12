import { useTranslation } from "react-i18next"
import {
  ElecCertificateSnapshot,
  TransferCertificate,
  TransferCertificateFilter,
  TransferCertificateStatus,
} from "../../types"
import { formatDate, formatNumber } from "common/utils/formatters"
import { Column } from "common/components/table2"
import { Tab } from "common/components/tabs2"
import useEntity from "common/hooks/entity"
import { compact } from "common/utils/collection"
import { useParams } from "react-router-dom"

export function useStatus() {
  const params = useParams<"status">()
  return (params.status ?? "pending") as TransferCertificateStatus
}

export function useTabs(snapshot?: ElecCertificateSnapshot): Tab<string>[] {
  const { t } = useTranslation()
  return [
    {
      key: "pending",
      label: t("En attente"),
      icon: "fr-icon-time-line",
      iconActive: "fr-icon-time-fill",
      path: "../transfer/pending",
      count: snapshot?.transfer_certificates_pending,
    },
    {
      key: "accepted",
      label: t("Accepté"),
      icon: "fr-icon-success-line",
      iconActive: "fr-icon-success-fill",
      path: "../transfer/accepted",
      count: snapshot?.transfer_certificates_accepted,
    },
    {
      key: "rejected",
      label: t("Refusé"),
      icon: "fr-icon-error-line",
      iconActive: "fr-icon-error-fill",
      path: "../transfer/rejected",
      count: snapshot?.transfer_certificates_rejected,
    },
  ]
}

export function useFilters() {
  const { t } = useTranslation()
  const entity = useEntity()

  const filters: Record<string, string> = {
    [TransferCertificateFilter.month]: t("Mois"),
    [TransferCertificateFilter.cpo]: t("Aménageur"),
    [TransferCertificateFilter.operator]: t("Redevable"),
    [TransferCertificateFilter.used_in_tiruert]: t("Décl. TIRUERT"),
  }

  if (entity.isCPO) {
    delete filters[TransferCertificateFilter.cpo]
    delete filters[TransferCertificateFilter.used_in_tiruert]
  }

  if (entity.isOperator) {
    delete filters[TransferCertificateFilter.operator]
  }

  return filters
}

export function useColumns() {
  const { t } = useTranslation()
  const entity = useEntity()

  return compact([
    !entity.isCPO && {
      key: "cpo",
      header: t("Aménageur"),
      cell: (p) => p.supplier.name,
    },
    !entity.isOperator && {
      key: "operator",
      header: t("Redevable"),
      cell: (p) => p.client.name,
    },
    {
      key: "transfer_date",
      header: t("Date d'émission"),
      cell: (p) => formatDate(p.transfer_date),
    },
    !entity.isCPO && {
      key: "consumption_date",
      header: t("Date de décl. TIRUERT"),
      cell: (p) => formatDate(p.consumption_date ?? null),
    },
    {
      key: "energy_amount",
      header: t("Quantité (MWh)"),
      cell: (p) => `${formatNumber(p.energy_amount)}`,
    },
  ]) satisfies Column<TransferCertificate>[]
}
