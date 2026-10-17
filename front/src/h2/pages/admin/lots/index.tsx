import { useH2LotsPage } from "h2/pages/lots/lots.hooks"
import { ActionsPage } from "traceability/components/actions-page"
import { useActionColumns } from "traceability/hooks/use-action-columns"
import { useActionFilters } from "traceability/hooks/use-action-filters"

const AdminLotsPage = () => {
  const { page } = useH2LotsPage()
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

export default AdminLotsPage
