import { useTranslation } from "react-i18next"
import {
  ElecCertificateSnapshot,
  ProvisionCertificate,
  ProvisionCertificateFilter,
  ProvisionCertificateStatus,
} from "../../types"
import { formatNumber } from "common/utils/formatters"
import { Column } from "common/components/table2"
import { Tab } from "common/components/tabs2"
import useEntity from "common/hooks/entity"
import { compact } from "common/utils/collection"
import { useParams } from "react-router-dom"
import { getSourceLabel } from "../../utils"

export function useStatus() {
  const params = useParams<"status">()
  return (params.status ?? "available") as ProvisionCertificateStatus
}

export function useTabs(
  snapshot?: ElecCertificateSnapshot
): Tab<ProvisionCertificateStatus>[] {
  const { t } = useTranslation()
  return [
    {
      key: "available",
      label: t("Disponible"),
      icon: "fr-icon-time-line",
      iconActive: "fr-icon-time-fill",
      path: "../provision/available",
      count: snapshot?.provision_certificates_available,
    },
    {
      key: "history",
      label: t("Historique"),
      icon: "fr-icon-booklet-line",
      iconActive: "fr-icon-booklet-fill",
      path: "../provision/history",
      count: snapshot?.provision_certificates_history,
    },
  ]
}

export function useFilters() {
  const { t } = useTranslation()
  const entity = useEntity()

  const filters: Record<string, string> = {
    [ProvisionCertificateFilter.cpo]: t("Aménageur"),
    [ProvisionCertificateFilter.quarter]: t("Trimestre"),
    [ProvisionCertificateFilter.operating_unit]: t("Unité d'exploitation"),
    [ProvisionCertificateFilter.source]: t("Source"),
  }

  if (entity.isCPO) {
    delete filters[ProvisionCertificateFilter.cpo]
  }

  return filters
}

export function useColumns() {
  const { t } = useTranslation()
  const entity = useEntity()

  return compact([
    {
      key: "quarter",
      header: t("Trimestre"),
      cell: (p) =>
        t("T{{quarter}} {{year}}", { quarter: p.quarter, year: p.year }),
    },
    (entity.isAdmin || entity.isExternal) && {
      key: "cpo",
      header: t("Aménageur"),
      cell: (p) => p.cpo.name,
    },
    {
      key: "operating_unit",
      header: t("Unité d'exploitation"),
      cell: (p) => p.operating_unit,
    },
    {
      key: "source",
      header: t("Source"),
      cell: (p) => getSourceLabel(p.source),
    },
    {
      key: "remaining_energy_amount",
      header: t("Quantité disponible (MWh)"),
      cell: (p) => `${formatNumber(p.remaining_energy_amount)}`,
    },
  ]) satisfies Column<ProvisionCertificate>[]
}
