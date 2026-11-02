import { useH2CertificatesPage } from "h2/pages/certificates/certificates.hooks"
import { ActionsPage } from "traceability/components/actions-page"
import { useActionColumns } from "traceability/hooks/action-columns"
import { useActionFilters } from "traceability/hooks/use-action-filters"

const AdminCertificatesPage = () => {
  const { page } = useH2CertificatesPage()
  const columns = useActionColumns()
  const filters = useActionFilters()

  return (
    <ActionsPage
      {...page}
      columns={[columns.holder, ...page.columns]}
      filters={[filters.holder, ...page.filters]}
    />
  )
}

export default AdminCertificatesPage
