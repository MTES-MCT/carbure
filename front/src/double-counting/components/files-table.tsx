import { useTranslation } from "react-i18next"
import { DoubleCountingApplicationDetails } from "../types"
import { getDoubleCountingAgreementDownloadLink } from "double-counting/api"

import useEntity from "common/hooks/entity"
import { useQuery } from "common/hooks/async"
import { Column, Table } from "common/components/table2"
import { NoResult } from "common/components/no-result2"
import { Button } from "common/components/button2"
import { Text } from "common/components/text"
import { apiTypes } from "common/services/api-fetch.types"
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
  const files = result?.data ?? []

  const columns: Column<apiTypes["AgreementDownloadLink"]>[] = [
    {
      header: t("Nom"),
      cell: (row) => row.name,
    },
    {
      header: t("Action"),
      cell: (row) =>
        row.link ? (
          <Button
            linkProps={{ href: row.link, target: "_blank" }}
            customPriority="link"
          >
            {t("Télécharger")}
          </Button>
        ) : (
          <Text>{t("Aucun fichier disponible")}</Text>
        ),
    },
  ]

  return !loading && files?.length === 0 ? (
    <NoResult label={t("Aucun fichier disponible")} />
  ) : (
    <Table columns={columns} rows={files} loading={loading} />
  )
}
