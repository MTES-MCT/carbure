import { ActionsPage } from "traceability/components/actions-page"

import { useLiableCertificatesPage } from "./liable-certificates.hooks"

const LiableCertificatesPage = () => {
  const { page } = useLiableCertificatesPage()

  return <ActionsPage {...page} />
}

export default LiableCertificatesPage
