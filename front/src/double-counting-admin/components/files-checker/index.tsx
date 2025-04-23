import { Notice } from "common/components/notice"
import { usePortal } from "common/components/portal"
import { Content, Main } from "common/components/scaffold"
import { Table, Cell, Column } from "common/components/table2"
import { Tabs } from "common/components/tabs2"
import useTitle from "common/hooks/title"
import {
  CheckDoubleCountingFilesResponse,
  DoubleCountingFileInfo,
} from "double-counting/types"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { useLocation } from "react-router-dom"
import ErrorsDetailsDialog from "../../../double-counting/components/application-checker/errors-details-dialog"
import FilesCheckerUploadButton from "./upload-button"
import ValidDetailsDialog from "../../../double-counting/components/application-checker/valid-details-dialog"
import { usePrivateNavigation } from "common/layouts/navigation"
import Badge from "@codegouvfr/react-dsfr/Badge"

const DoubleCountingFilesChecker = () => {
  const { t } = useTranslation()
  const location = useLocation()
  useTitle(t("Vérification de fichiers de double comptage"))
  usePrivateNavigation("Vérification de fichiers de double comptage")
  const portal = usePortal()

  const checkedFiles: CheckDoubleCountingFilesResponse =
    location.state?.checkedFiles

  const filesValid = checkedFiles?.files.filter((f) => !f.error_count) || []
  const filesToFix = checkedFiles?.files.filter((f) => f.error_count > 0) || []
  const valid = { count: filesValid.length, files: filesValid }
  const toFix = { count: filesToFix.length, files: filesToFix }
  const [tab, setTab] = useState(filesToFix.length > 0 ? "to-fix" : "valid")

  const files: FileList = location.state?.files

  function showFileErrorsDialog(fileData: DoubleCountingFileInfo) {
    portal((close) => (
      <ErrorsDetailsDialog fileData={fileData} onClose={close} />
    ))
  }

  function showFileValidDialog(fileData: DoubleCountingFileInfo) {
    const file = Array.from(files).find(
      (f) =>
        f.name.replace(/[^a-zA-Z0-9-]/g, "") ===
        fileData.file_name.replace(/[^a-zA-Z0-9-]/g, "")
    )
    if (!file) return
    portal((close) => (
      <ValidDetailsDialog fileData={fileData} onClose={close} file={file} />
    ))
  }

  const columns: Column<DoubleCountingFileInfo>[] = [
    {
      header: t("Statut"),
      cell: (file) =>
        file.error_count ? (
          <Badge severity="warning">{t("À corriger")}</Badge>
        ) : (
          <Badge severity="success">{t("Valide")}</Badge>
        ),
    },
    {
      header: t("Erreurs"),
      cell: (file) => (
        <Cell
          text={t("{{errorCount}} erreurs", { errorCount: file.error_count })}
        />
      ),
    },
    {
      header: t("fichier"),
      cell: (file) => <Cell text={file.file_name} />,
    },
    {
      header: t("Site de production"),
      cell: (file) => <Cell text={file.production_site} />,
    },
    {
      header: t("Période de validité"),
      cell: (file) => (
        <Cell
          text={
            file.start_year
              ? `${file.start_year} - ${file.start_year + 1}`
              : t("Non reconnue")
          }
        />
      ),
    },
  ]

  return (
    <Main>
      <header>
        <FilesCheckerUploadButton label={t("Vérifier d'autres demandes")} />

        {checkedFiles && (
          <Tabs
            onFocus={setTab}
            focus={tab}
            tabs={[
              {
                key: "to-fix",
                label: t("À corriger ({{toFixCount}})", {
                  toFixCount: toFix.count,
                }),
              },
              {
                key: "valid",
                label: t("Valides ({{validCount}})", {
                  validCount: valid.count,
                }),
              },
            ]}
          />
        )}
      </header>
      <Content>
        {!checkedFiles && (
          <Notice variant="warning" icon="ri-alert-line">
            {t(
              "Aucune données à vérifier. Merci d'envoyer de nouveaux fichiers à analyser."
            )}
          </Notice>
        )}

        {checkedFiles && (
          <>
            {tab === "valid" && (
              <>
                {valid.count === 0 && (
                  <Notice variant="warning" icon="ri-alert-line">
                    {t("Aucun dossier valide")}
                  </Notice>
                )}

                {valid.count > 0 && (
                  <Table
                    columns={columns}
                    rows={valid.files}
                    onAction={showFileValidDialog}
                  />
                )}
              </>
            )}

            {tab === "to-fix" && (
              <>
                {toFix.count === 0 && (
                  <Notice variant="warning" icon="ri-alert-line">
                    {t("Aucun dossier à corriger !")}
                  </Notice>
                )}

                {toFix.count > 0 && (
                  <Table
                    columns={columns}
                    rows={toFix.files}
                    onAction={showFileErrorsDialog}
                  />
                )}
              </>
            )}
          </>
        )}
      </Content>
    </Main>
  )
}

export default DoubleCountingFilesChecker
