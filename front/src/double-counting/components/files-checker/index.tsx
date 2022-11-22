import Alert from "common/components/alert"
import { AlertCircle } from "common/components/icons"
import { Main } from "common/components/scaffold"
import Table, { Cell, Column } from "common/components/table"
import Tabs from "common/components/tabs"
import useTitle from "common/hooks/title"
import { DoubleCountingFileInfo } from "double-counting/types"
import { useState } from "react"
import { useTranslation } from "react-i18next"

const DoubleCountingFilesChecker = () => {
  const { t } = useTranslation()
  useTitle(t("Vérification de fichiers de double comptage"))
  const [tab, setTab] = useState("accepted")

  function showFileErrorsDialog(file: DoubleCountingFileInfo) {
    //TODO open FIle error detail dialog
  }

  const columns: Column<DoubleCountingFileInfo>[] = [
    {
      header: t("Statut"),
      cell: (file) => <p>Tag</p>,
    },
    {
      header: t("Erreurs"),
      cell: (file) => <Cell text={"Nombre d'erreurr"} />,
    },
    {
      header: t("Producteur"),
      cell: (file) => <Cell text={"nom du producteur"} />,
    },
    {
      header: t("Site de production"),
      cell: (file) => <Cell text={"nom du site de prod"} />,
    },
    {
      header: t("Période de validité"),
      cell: (a) => <Cell text={"Period de validité"} />,
    },
  ]

  const checked = { count: 0, files: [] }
  const toFix = { count: 0, files: [] }
  return (
    <Main>
      <header>
        <section>
          <Tabs
            variant="switcher"
            onFocus={setTab}
            tabs={[
              { key: "checked", path: "checked", label: t("Valides") },
              { key: "to-fix", path: "to-fix", label: t("À corriger") },
            ]}
          />
        </section>
      </header>

      {tab === "checked" && (
        <>
          {checked.count === 0 && (
            <Alert variant="warning" icon={AlertCircle}>
              {t("Aucun dossier valide")}
            </Alert>
          )}

          {checked.count > 0 && (
            <Table columns={columns} rows={checked.files} />
          )}
        </>
      )}

      {tab === "to-fix" && (
        <>
          {toFix.count === 0 && (
            <Alert variant="warning" icon={AlertCircle}>
              {t("Aucun dossier à corriger !")}
            </Alert>
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
    </Main>
  )
}

export default DoubleCountingFilesChecker
