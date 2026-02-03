import { Cell, Column } from "common/components/table2"
import { useTranslation } from "react-i18next"
import Tag from "@codegouvfr/react-dsfr/Tag"
import { getDepartmentName } from "common/utils/geography"
import { getBiomethaneAdminDashboardFilters } from "../api"
import { defaultNormalizer } from "common/utils/normalize"
import { formatDate } from "common/utils/formatters"
import { AnnualDeclarationStatusBadge } from "biomethane/components/annual-declaration-status-badge"
import { BiomethaneAdminAnnualDeclarationFilters } from "../types"
import type {
  BiomethaneAdminAnnualDeclaration,
  BiomethaneAdminDashboardQuery,
} from "../types"
import { AnnualDeclarationStatus } from "biomethane/types"
import { useTariffReferenceOptions } from "biomethane/pages/contract/components/contract-infos/contract-infos.hooks"
import { useCallback } from "react"

export const useDashboardColumns =
  (): Column<BiomethaneAdminAnnualDeclaration>[] => {
    const { t } = useTranslation()
    const tariffReferenceOptions = useTariffReferenceOptions()
    const getTariffReferenceLabel = useCallback(
      (value: string) => {
        return (
          tariffReferenceOptions.find((option) => option.value === value)
            ?.label ?? value
        )
      },
      [tariffReferenceOptions]
    )
    return [
      {
        header: t("Installation"),
        cell: (row) => <Cell text={row.producer.name} />,
      },
      {
        header: t("Mise en service"),
        cell: (row) => (
          <Cell
            text={row.effective_date ? formatDate(row.effective_date) : "-"}
          />
        ),
      },
      {
        header: t("Arrêté tarifaire"),
        cell: (row) => (
          <Cell
            text={
              row.tariff_reference
                ? getTariffReferenceLabel(row.tariff_reference)
                : "-"
            }
          />
        ),
      },
      {
        header: t("Département"),
        cell: (row) =>
          row.department && (
            <Tag
              small
            >{`${row.department} - ${getDepartmentName(row.department) ?? "-"}`}</Tag>
          ),
      },
      {
        header: t("Statut"),
        cell: (row) => (
          <AnnualDeclarationStatusBadge
            status={row.status as AnnualDeclarationStatus}
          />
        ),
        style: {
          minWidth: "260px",
        },
      },
    ]
  }

export const useGetDashboardFilterOptions = (
  query: BiomethaneAdminDashboardQuery
) => {
  const { t } = useTranslation()

  const filterLabels: Record<BiomethaneAdminAnnualDeclarationFilters, string> =
    {
      [BiomethaneAdminAnnualDeclarationFilters.status]: t("Statut"),
      [BiomethaneAdminAnnualDeclarationFilters.tariff_reference]:
        t("Arrêté tarifaire"),
      [BiomethaneAdminAnnualDeclarationFilters.department]: t("Départements"),
    }

  const statusLabel = (value: string) => {
    switch (value) {
      case "DECLARED":
        return t("Déclaration transmise")
      case "IN_PROGRESS":
        return t("Déclaration en cours")
      case "OVERDUE":
        return t("Déclaration en retard")
      default:
        return value
    }
  }

  const normalizers = {
    [BiomethaneAdminAnnualDeclarationFilters.status]: (value: string) => ({
      value,
      label: statusLabel(value),
    }),
    [BiomethaneAdminAnnualDeclarationFilters.tariff_reference]: (
      value: string
    ) => defaultNormalizer(value),
    [BiomethaneAdminAnnualDeclarationFilters.department]: (value: string) => ({
      value,
      label: `${value} - ${getDepartmentName(value) ?? value}`,
    }),
  }

  return {
    normalizers,
    filterLabels,
    getFilterOptions: (filter: BiomethaneAdminAnnualDeclarationFilters) =>
      getBiomethaneAdminDashboardFilters(query, filter),
  }
}
