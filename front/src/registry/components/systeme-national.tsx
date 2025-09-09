import { findSystemNationalCertificates } from "common/api"
import { SearchInput } from "common/components/input"
import Table from "common/components/table"
import { useQuery } from "common/hooks/async"
import { formatDate } from "common/utils/formatters"
import { useState } from "react"
import { useTranslation } from "react-i18next"

export const SystemeNational = () => {
  const { t } = useTranslation()

  const [query, setQuery] = useState<string | undefined>("")

  const certificates = useQuery(findSystemNationalCertificates, {
    key: "systeme-national",
    params: [query ?? ""],
  })

  return (
    <>
      <SearchInput
        clear
        debounce={250}
        label={t("Rechercher un certificat ou une société")}
        value={query}
        onChange={setQuery}
      />

      <Table
        loading={certificates.loading}
        rows={certificates.result ?? []}
        columns={[
          {
            key: "certificate_id",
            header: t("Numéro d'adhésion"),
            cell: (e) => e.certificate_id,
            orderBy: (e) => e.certificate_id,
          },
          {
            key: "entity",
            header: t("Société"),
            cell: (e) => e.certificate_holder,
            orderBy: (e) => e.certificate_holder,
          },
          {
            key: "validity",
            header: t("Validité"),
            cell: (e) =>
              `${formatDate(e.valid_from)} - ${formatDate(e.valid_until)}`,
            orderBy: (e) => e.valid_from,
          },
          {
            key: "scope",
            header: t("Catégorie(s)"),
            cell: (e) => String(e.scope),
            orderBy: (e) => String(e.scope),
          },
        ]}
      />
    </>
  )
}
