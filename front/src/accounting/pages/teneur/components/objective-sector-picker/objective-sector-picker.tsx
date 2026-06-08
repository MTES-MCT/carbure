import { useTranslation } from "react-i18next"
import { Autocomplete } from "common/components/autocomplete2"
import { useBind } from "common/components/form2"
import { SectorObjective } from "../../types"
import { formatSector } from "accounting/utils/formatters"

type ObjectiveSectorPickerProps = {
  sectorObjectives: SectorObjective[]
}

export const ObjectiveSectorPicker = ({
  sectorObjectives,
}: ObjectiveSectorPickerProps) => {
  const { t } = useTranslation()
  const bind = useBind<{ objective_sector: string | undefined }>()

  return (
    <Autocomplete
      {...bind("objective_sector")}
      label={t(
        "Choisissez une filière afin d'affecter ce certificat de teneur à l'objectif correspondant :"
      )}
      options={sectorObjectives.map((sector) => ({
        value: sector.code,
        label: formatSector(sector.code),
      }))}
    />
  )
}
