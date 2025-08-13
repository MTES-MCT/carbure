import { Column, Cell } from "common/components/table2"
import { useTranslation } from "react-i18next"
import {
  ElecDataQualichargeOverview,
  QualichargeFilter,
  QualichargeQuery,
  QualichargeTab,
  QualichargeValidatedBy,
} from "./types"
import { QualichargeBadge } from "./components/qualicharge-badge"
import { formatDate } from "common/utils/formatters"
import { getQualichargeFilters, getYears } from "./api"
import { formatQualichargeStatus } from "./formatters"
import { compact } from "common/utils/collection"
import useEntity from "common/hooks/entity"
import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "common/hooks/query-builder-2"
import useYears from "common/hooks/years-2"
import { useMatch } from "react-router-dom"
import { ExternalAdminPages } from "common/types"

export const useQualichargeColumns = (status: QualichargeTab) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const columns: Column<ElecDataQualichargeOverview>[] = compact([
    status === QualichargeTab.PENDING && {
      header: t("Statut"),
      cell: (data) => <QualichargeBadge status={data.validated_by} />,
      style: {
        minWidth: "240px",
      },
    },
    (entity.isAdmin || entity.hasAdminRight(ExternalAdminPages.ELEC)) && {
      header: t("Aménageur"),
      cell: (data) => <Cell text={data.cpo.name} />,
    },
    {
      header: t("Unité d'exploitation"),
      cell: (data) => <Cell text={data.operating_unit} />,
    },
    {
      header: t("Station ID"),
      cell: (data) => <Cell text={data.station_id} />,
    },
    {
      header: t("Début de la mesure"),
      cell: (data) => <Cell text={formatDate(data.date_from)} />,
    },
    {
      header: t("Fin de la mesure"),
      cell: (data) => <Cell text={formatDate(data.date_to)} />,
    },
    {
      header: t("Energie (MWh)"),
      cell: (data) => <Cell text={data.energy_amount} />,
    },
  ])

  return columns
}

export const useGetFilterOptions = (query: QualichargeQuery) => {
  const getFilterOptions = async (filter: string) => {
    const data = await getQualichargeFilters(query, filter as QualichargeFilter)

    if (filter === QualichargeFilter.validated_by) {
      return data
        .filter((item) => item !== QualichargeValidatedBy.BOTH)
        .map((item) => ({
          label: formatQualichargeStatus(item as QualichargeValidatedBy),
          value: item,
        }))
    }

    return data
  }

  return getFilterOptions
}

const useStatus = () => {
  const match = useMatch(
    "/org/:entity/charge-points/qualicharge/:year/:status/*"
  )
  return (match?.params.status ?? QualichargeTab.PENDING) as QualichargeTab
}

export const useQualichargeQueryBuilder = () => {
  const entity = useEntity()
  const status = useStatus()
  const years = useYears("/qualicharge", getYears)
  const [state, actions] = useCBQueryParamsStore(entity, years.selected, status)

  const query = useCBQueryBuilder(state)

  return { state, actions, query, status, years }
}
