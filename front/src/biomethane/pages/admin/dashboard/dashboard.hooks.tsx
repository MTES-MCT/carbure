import { Cell, Column } from "common/components/table2"
import { useTranslation } from "react-i18next"
import Tag from "@codegouvfr/react-dsfr/Tag"
import { getDepartmentName } from "common/utils/geography"
import { getBiomethaneAdminDashboardFilters } from "../api"
import { formatDate } from "common/utils/formatters"
import { AnnualDeclarationStatusBadge } from "biomethane/components/annual-declaration-status-badge"
import { BiomethaneAdminAnnualDeclarationFilters } from "../types"
import type {
  BiomethaneAdminAnnualDeclaration,
  BiomethaneAdminDashboardQuery,
} from "../types"
import { AnnualDeclarationStatus } from "biomethane/types"
import { useGetTariffReferenceLabel } from "biomethane/pages/contract/components/contract-infos/contract-infos.hooks"
import { getDeclarationStatusLabel } from "biomethane/utils"
import { TariffReference } from "biomethane/pages/contract/types"

export const useDashboardColumns =
  (): Column<BiomethaneAdminAnnualDeclaration>[] => {
    const { t } = useTranslation()
    const getTariffReferenceLabel = useGetTariffReferenceLabel()
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
  const getTariffReferenceLabel = useGetTariffReferenceLabel()
  const filterLabels: Record<BiomethaneAdminAnnualDeclarationFilters, string> =
    {
      [BiomethaneAdminAnnualDeclarationFilters.status]: t("Statut"),
      [BiomethaneAdminAnnualDeclarationFilters.tariff_reference]:
        t("Arrêté tarifaire"),
      [BiomethaneAdminAnnualDeclarationFilters.department]: t("Départements"),
    }

  const normalizers = {
    [BiomethaneAdminAnnualDeclarationFilters.status]: (value: string) => ({
      value,
      label: getDeclarationStatusLabel(value as AnnualDeclarationStatus),
    }),
    [BiomethaneAdminAnnualDeclarationFilters.tariff_reference]: (
      value: string
    ) => ({
      value,
      label: getTariffReferenceLabel(value as TariffReference),
    }),
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
