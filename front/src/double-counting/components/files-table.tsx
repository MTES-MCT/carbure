import { useTranslation } from "react-i18next"
import { DoubleCountingApplicationDetails } from "../types"
import { getDoubleCountingAgreementDownloadLink } from "double-counting/api"

import useEntity from "common/hooks/entity"
import { useQuery } from "common/hooks/async"
import { Column, Table } from "common/components/table2"
import { NoResult } from "common/components/no-result2"
type FilesTableProps = {
  application: DoubleCountingApplicationDetails
}

export const FilesTable = ({ application }: FilesTableProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { loading, result } = useQuery(
    () => getDoubleCountingAgreementDownloadLink(entity.id, application.id),
    {
      key: "double-counting-agreement-download-link",
      params: [],
    }
  )
  const file = result?.data

  const rows = [
    {
      name: "Demande d'agrément",
      url: file?.download_link,
    },
  ]

  const columns: Column<{
    name: string
    url?: string
  }>[] = [
    {
      header: t("Nom"),
      cell: (row) => row.name,
    },
    {
      header: t("Action"),
      cell: (row) => row.url,
    },
  ]

  return !loading && !file?.download_link ? (
    <NoResult label={t("Aucun fichier disponible")} />
  ) : (
    <Table columns={columns} rows={rows} loading={loading} />
  )
}
