import { ActionsPage } from "traceability/components/actions-page"

import { useH2LotsPage } from "./lots.hooks"

const LotsPage = () => {
  const { page, excelImport, detailActions } = useH2LotsPage()

  return (
    <ActionsPage
      {...page}
      excelImport={excelImport}
      detailActions={detailActions}
    />
  )
}

export default LotsPage
