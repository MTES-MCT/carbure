import { Button } from "common/components/button2"
import { usePortal } from "common/components/portal"
import { Box, Divider, Row } from "common/components/scaffold"
import { Title } from "common/components/title"
import { useTranslation } from "react-i18next"
import { FileUploadDialog } from "./file-upload-dialog"
import { DoubleCountingFile } from "double-counting/types"
import { NoResult } from "common/components/no-result2"
import { Table, Column } from "common/components/table2"
import { Confirm } from "common/components/dialog2"
import { Text } from "common/components/text"
import { FileTypeEnum } from "api-schema"

type FilesManagerProps = {
  readOnly?: boolean
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
      file_name: file.name,
      file_type: FileTypeEnum.EXTRA,
      url: URL.createObjectURL(file),
    }))

    onAddFiles?.(dcFiles)
  }

  const columns: Column<DoubleCountingFile>[] = [
    {
      header: t("Nom"),
      cell: (row) => row.file_name,
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

  if (!file.url) {
    return <Text>{t("Aucun fichier disponible")}</Text>
  }

  return (
    <Row style={{ gap: "var(--spacing-xs)" }}>
      <Button
        iconId="fr-icon-download-fill"
        linkProps={{ href: file.url, target: "_blank" }}
        priority="secondary"
        title={t("Télécharger")}
        size="small"
      />
      {!readOnly && file.file_type !== "EXCEL" && (
        <Button
          iconId="fr-icon-delete-fill"
          size="small"
          priority="secondary"
          title={t("Supprimer")}
          onClick={() =>
            portal((close) => (
              <Confirm
                title={t("Supprimer le fichier")}
                description={t("Voulez-vous supprimer le fichier {{file}} ?", {
                  file: file.file_name,
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
