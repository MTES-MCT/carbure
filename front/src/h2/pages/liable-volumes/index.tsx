import { ActionsPage } from "traceability/components/actions-page"

import { useLiableVolumesPage } from "./liable-volumes.hooks"

const LiableVolumesPage = () => {
  const { page } = useLiableVolumesPage()

  return <ActionsPage {...page} />
}

export default LiableVolumesPage
