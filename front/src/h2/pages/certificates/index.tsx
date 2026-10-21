import { ActionsPage } from "traceability/components/actions-page"

import { useH2CertificatesPage } from "./certificates.hooks"

const CertificatesPage = () => {
  const { page } = useH2CertificatesPage()

  return <ActionsPage {...page} />
}

export default CertificatesPage
