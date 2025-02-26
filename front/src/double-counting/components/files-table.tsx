import { useTranslation } from "react-i18next"
import { DoubleCountingApplicationDetails } from "../types"
import { Link } from "react-router-dom"
import { useEffect } from "react"
import { getDoubleCountingAgreementDownloadLink } from "double-counting/api"
import { useState } from "react"
import useEntity from "common/hooks/entity"
type FilesTableProps = {
  application: DoubleCountingApplicationDetails
}

export const FilesTable = ({ application }: FilesTableProps) => {
  const { t } = useTranslation()
  const [downloadLink, setDownloadLink] = useState<string | null>(null)
  const entity = useEntity()

  useEffect(() => {
    getDoubleCountingAgreementDownloadLink(entity.id, application.id).then(
      (res) => {
        setDownloadLink(res.data?.download_link ?? null)
      }
    )
  }, [application.id])

  return (
    <section>
      <h1>Dossier</h1>
      <div style={{ marginLeft: 16 }}>
        {downloadLink ? (
          <Link to={downloadLink} target="_blank">
            {t("Télécharger le dossier")}
          </Link>
        ) : (
          <p>{t("Pas de lien disponible")}</p>
        )}
      </div>
    </section>
  )
}
