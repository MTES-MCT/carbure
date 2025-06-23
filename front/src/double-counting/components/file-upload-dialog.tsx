import { Dialog } from "common/components/dialog2"
import { useTranslation } from "react-i18next"
import { Button } from "common/components/button2"
import { FileListInput } from "common/components/inputs2"
import { useState } from "react"

type FileUploadDialogProps = {
  onConfirm: (files: FileList) => void
  onClose: () => void
}

export const FileUploadDialog = ({
  onConfirm,
  onClose,
}: FileUploadDialogProps) => {
  const { t } = useTranslation()

  const [files, setFiles] = useState<FileList>()

  return (
    <Dialog
      onClose={onClose}
      gap="lg"
      header={
        <Dialog.Title style={{ justifyContent: "space-between" }}>
          {t("Ajouter des fichiers relatifs à la demande")}
        </Dialog.Title>
      }
      footer={
        <Button
          disabled={!files}
          onClick={() => {
            onConfirm(files!)
            onClose()
          }}
        >
          {t("Confirmer")}
        </Button>
      }
    >
      <FileListInput
        label={t("Vous pouvez sélectionner un ou plusieurs fichiers.")}
        placeholder={t("Choisir des fichiers")}
        value={files}
        onChange={setFiles}
      />

      <ul>
        {Array.from(files ?? []).map((file) => (
          <li key={file.name}>{file.name}</li>
        ))}
      </ul>
    </Dialog>
  )
}
