import { FileInput } from "common/components/inputs2"
import { Box } from "common/components/scaffold"
import { useTranslation } from "react-i18next"

type AddIndustrialWastesProps = {
  industrialWastesFile?: File
  setIndustrialWastesFile: (file?: File) => void
}
export const AddIndustrialWastes = ({
  industrialWastesFile,
  setIndustrialWastesFile,
}: AddIndustrialWastesProps) => {
  const { t } = useTranslation()
  return (
    <Box>
      <FileInput
        label={t(
          "Déposer le fichier relatif aux déchets industriels et au CIVE."
        )}
        placeholder={t("Choisir un fichier")}
        value={industrialWastesFile}
        onChange={setIndustrialWastesFile}
      />
    </Box>
  )
}
