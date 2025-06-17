import { useTranslation } from "react-i18next"
import {
  ProvisionCertificate,
  ProvisionCertificateFilter,
  ProvisionCertificateSource,
  ProvisionCertificateStatus,
} from "./types"
import { formatNumber } from "common/utils/formatters"
import { Columns } from "common/components/table2"
import { Tab } from "common/components/tabs2"

export function useTabs(): Tab<ProvisionCertificateStatus>[] {
  const { t } = useTranslation()
  return [
    {
      key: "available",
      label: t("Disponible"),
      icon: "fr-icon-time-line",
      iconActive: "fr-icon-time-fill",
      path: "../provision/available",
    },
    {
      key: "history",
      label: t("Historique"),
      icon: "fr-icon-booklet-line",
      iconActive: "fr-icon-booklet-fill",
      path: "../provision/history",
    },
  ]
}

export function useFilters() {
  const { t } = useTranslation()
  return {
    [ProvisionCertificateFilter.Quarter]: t("Période"),
    [ProvisionCertificateFilter.OperatingUnit]: t("Unité d'exploitation"),
    [ProvisionCertificateFilter.Source]: t("Source"),
  }
}

export function useColumns() {
  const { t } = useTranslation()

  const sources = {
    [ProvisionCertificateSource.MANUAL]: t("DGEC"),
    [ProvisionCertificateSource.METER_READINGS]: t("Relevés trimestriels"),
    [ProvisionCertificateSource.QUALICHARGE]: t("Qualicharge"),
  }

  return {
    period: {
      key: "quarter",
      header: t("Période"),
      cell: (p) =>
        t("T{{quarter}} {{year}}", { quarter: p.quarter, year: p.year }),
    },

    operatingUnit: {
      key: "operating_unit",
      header: t("Unité d'exploitation"),
      cell: (p) => p.operating_unit,
    },

    source: {
      key: "source",
      header: t("Source"),
      cell: (p) => (p.source ? sources[p.source] : t("N/A")),
    },

    energy: {
      key: "remaining_energy_amount",
      header: t("MWh"),
      cell: (p) =>
        p.remaining_energy_amount > 0.01 // not in history yet
          ? `${formatNumber(p.remaining_energy_amount, { fractionDigits: 0 })}`
          : `${formatNumber(p.energy_amount, { fractionDigits: 0 })}`,
    },
  } satisfies Columns<ProvisionCertificate>
}
