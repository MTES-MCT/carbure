import { ActionsPage } from "traceability/components/actions-page"

import { useH2LotsPage } from "./lots.hooks"

const LotsPage = () => {
  const { page, excelImport, renderDetailActions } = useH2LotsPage()

  return (
    <ActionsPage
      {...page}
      excelImport={excelImport}
      renderDetailActions={renderDetailActions}
    />
  )
}

export default LotsPage
