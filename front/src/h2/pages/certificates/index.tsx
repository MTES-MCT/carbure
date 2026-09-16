import { useTranslation } from "react-i18next"

import { ActionsPage } from "traceability/components/actions-page"
import { useActionColumns } from "traceability/hooks/action-columns"
import { useActionFilters } from "traceability/hooks/use-action-filters"
import { useActionFields } from "traceability/hooks/action-fields"
import { ActionIndustry, ActionQuery, ActionType } from "traceability/types"

const H2_CERTIFICATE_QUERY: Partial<ActionQuery> = {
  type: [ActionType.VALORIZE],
}

const CertificatesPage = () => {
  const { t } = useTranslation()

  const filters = useActionFilters()
  const columns = useActionColumns()
  const fields = useActionFields()

  return (
    <ActionsPage
      industry={ActionIndustry.H2}
      listTitle={t("Certificats d'hydrogène")}
      detailTitle={t("Certificat d'hydrogène n˚")}
      subpath="certificates"
      fixedQuery={H2_CERTIFICATE_QUERY}
      filters={[
        filters.period, //
      ]}
      columns={[
        { ...columns.pos_id, header: t("N˚ de certificat") },
        columns.working_date,
        columns.quantity,
        columns.total_emissions,
      ]}
      fieldsets={[
        {
          legend: t("Certificat"),
          fields: [
            fields.pos_id,
            { ...fields.energy, label: t("Quantité certifiée") },
            { ...fields.working_date, label: t("Date de création") },
          ],
        },
        {
          legend: t("Émissions/réductions"),
          fields: [
            fields.ei,
            fields.ep,
            fields.etd,
            fields.eu,
            fields.eccs,
            fields.total_emissions,
          ],
        },
      ]}
    />
  )
}

export default CertificatesPage
