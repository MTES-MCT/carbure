import { Button } from "common/components/button2"
import { usePortal } from "common/components/portal"
import { Box, Divider, Row } from "common/components/scaffold"
import { Title } from "common/components/title"
import { useTranslation } from "react-i18next"
import { FileUploadDialog } from "./file-upload-dialog"
import {
  DoubleCountingApplicationDetails,
  DoubleCountingFile,
} from "double-counting/types"
import { NoResult } from "common/components/no-result2"
import { Table, Column } from "common/components/table2"
import { Confirm } from "common/components/dialog2"
import { Text } from "common/components/text"

type FilesManagerProps = {
  readOnly?: boolean
  application?: DoubleCountingApplicationDetails
  files?: DoubleCountingFile[]
  onAddFiles?: (files: DoubleCountingFile[]) => void
  onDeleteFile?: (file: DoubleCountingFile) => void
}

export const FilesManager = ({
  readOnly,
  files = [],
  onAddFiles,
  onDeleteFile,
}: FilesManagerProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  function saveFiles(files: FileList) {
    const dcFiles = Array.from(files).map<DoubleCountingFile>((file) => ({
      id: 0,
      file,
      name: file.name,
      link: URL.createObjectURL(file),
    }))

    onAddFiles?.(dcFiles)
  }

  const columns: Column<DoubleCountingFile>[] = [
    {
      header: t("Nom"),
      cell: (row) => row.name,
    },
    {
      header: t("Actions"),
      style: { flex: "0 0 128px" },
      cell: (row) => (
        <FileActions file={row} readOnly={readOnly} onDelete={onDeleteFile} />
      ),
    },
  ]

  return (
    <Box>
      <Row style={{ justifyContent: "space-between", alignItems: "center" }}>
        <Title is="p" as="h6">
          {t("Fichiers associés à la demande")}
        </Title>

        {!readOnly && (
          <Button
            priority="secondary"
            iconId="fr-icon-download-fill"
            onClick={() =>
              portal((onClose) => (
                <FileUploadDialog onClose={onClose} onConfirm={saveFiles} />
              ))
            }
          >
            {t("Charger des fichiers")}
          </Button>
        )}
      </Row>
      <Divider noMargin />
      {files.length === 0 ? (
        <NoResult label={t("Aucun fichier disponible")} />
      ) : (
        <Table columns={columns} rows={files} />
      )}
    </Box>
  )
}

type FileActionProps = {
  file: DoubleCountingFile
  readOnly?: boolean
  onDelete?: (file: DoubleCountingFile) => void
}

export const FileActions = ({ file, readOnly, onDelete }: FileActionProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  if (!file.link) {
    return <Text>{t("Aucun fichier disponible")}</Text>
  }

  return (
    <Row style={{ gap: "var(--spacing-xs)" }}>
      <Button
        iconId="fr-icon-download-fill"
        linkProps={{ href: file.link, target: "_blank" }}
        priority="secondary"
        title={t("Télécharger")}
      />
      {!readOnly && file.id !== -1 && (
        <Button
          iconId="fr-icon-delete-fill"
          priority="secondary"
          title={t("Supprimer")}
          onClick={() =>
            portal((close) => (
              <Confirm
                title={t("Supprimer le fichier")}
                description={t("Voulez-vous supprimer le fichier {{file}} ?", {
                  file: file.name,
                })}
                confirm={t("Supprimer")}
                customVariant="danger"
                onClose={close}
                onConfirm={async () => {
                  onDelete?.(file)
                  close()
                }}
              />
            ))
          }
        />
      )}
    </Row>
  )
}
