import { useTranslation } from "react-i18next"

import { ActionsPage } from "traceability/components/actions-page"
import { useActionColumns } from "traceability/hooks/use-action-columns"
import { useActionFilters } from "traceability/hooks/use-action-filters"
import { useActionFields } from "traceability/hooks/use-action-fields"
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
        filters.year, //
      ]}
      columns={[
        { ...columns.pos_id, header: t("N˚ de certificat") },
        columns.working_date,
        columns.quantity,
        columns.total_emissions,
      ]}
      fields={[
        fields.pos_id,
        fields.holder,
        fields.quantity,
        fields.ei,
        fields.ep,
        fields.etd,
        fields.eu,
        fields.eccs,
        fields.total_emissions,
      ]}
    />
  )
}

export default CertificatesPage
