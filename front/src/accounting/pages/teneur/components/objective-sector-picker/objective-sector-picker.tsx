import { useTranslation } from "react-i18next"
import { Autocomplete } from "common/components/autocomplete2"
import { OperationSector } from "accounting/types"

type ObjectiveSectorPickerProps = {
  value: OperationSector | undefined
  onChange: (sector: OperationSector | undefined) => void
}

export const ObjectiveSectorPicker = ({
  value,
  onChange,
}: ObjectiveSectorPickerProps) => {
  const { t } = useTranslation()

  return (
    <Autocomplete
      value={value}
      onChange={onChange}
      label={t(
        "Choisissez une filière afin d'affecter ce certificat de teneur à l'objectif correspondant :"
      )}
      options={[
        { value: OperationSector.ESSENCE, label: "Essence" },
        { value: OperationSector.GAZOLE, label: "Gazole" },
      ]}
    />
  )
}
