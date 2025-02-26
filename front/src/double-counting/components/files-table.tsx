import { useTranslation } from "react-i18next"
import { DoubleCountingApplicationDetails } from "../types"
import { Link } from "react-router-dom"

type FilesTableProps = {
  application: DoubleCountingApplicationDetails
}

export const FilesTable = ({ application }: FilesTableProps) => {
  const { t } = useTranslation()

  return (
    <section>
      <h1>{t("Dossier")}</h1>
      <div style={{ marginLeft: 16 }}>
        {application.download_link ? (
          <Link to={application.download_link} target="_blank">
            {t("Télécharger le dossier")}
          </Link>
        ) : (
          <p>{t("Pas de lien disponible")}</p>
        )}
      </div>
    </section>
  )
}
