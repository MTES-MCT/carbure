import { t } from "i18next"
import { Trans } from "react-i18next"
import { DoubleCountingFileInfo } from "../../../double-counting/types"

const FileApplicationInfo = ({
  fileData,
  createdAt,
  entityName,
}: {
  fileData: DoubleCountingFileInfo
  createdAt?: string
  entityName?: string
}) => {
  return (
    <>
      <Trans
        values={{
          productionSite: fileData.production_site,
        }}
        defaults={`Pour le site de production {{productionSite}}`}
      />
      {entityName && ` ${t("de")} ${entityName}`}, {t("soumis par") + " "}
      <a href={`mailto:${fileData.producer_email}`}>
        {fileData.producer_email}
      </a>
      {createdAt && ` ${t("le")} ${createdAt}`}
    </>
  )
}
export default FileApplicationInfo
