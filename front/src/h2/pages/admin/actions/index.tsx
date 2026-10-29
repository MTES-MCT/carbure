import { ActionsPage } from "traceability/components/actions-page"

import { useH2AdminActionsPage } from "./actions.hooks"

const AdminActionsPage = () => {
  const page = useH2AdminActionsPage()

  return <ActionsPage {...page} />
}

export default AdminActionsPage
