import { ActionsPage } from "traceability/components/actions-page"

import { useH2VolumesPage } from "./volumes.hooks"

const VolumesPage = () => {
  const { page } = useH2VolumesPage()

  return <ActionsPage {...page} />
}

export default VolumesPage
