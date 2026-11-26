import { ActionsPage } from "traceability/components/actions-page"

import { useH2SentCertificatesPage } from "./sent-certificates.hooks"

const SentCertificatesPage = () => {
  const { page } = useH2SentCertificatesPage()

  return <ActionsPage {...page} />
}

export default SentCertificatesPage
