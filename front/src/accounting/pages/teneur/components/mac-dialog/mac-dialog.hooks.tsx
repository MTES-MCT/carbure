import { NumberInput } from "common/components/inputs2"
import { Column } from "common/components/table2"
import { formatDate } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { MacFossilFuel } from "../../api"
import css from "./mac-dialog.module.css"

type MacTableRow = {
  month: number
  monthLabel: string
  volumes: Partial<Record<string, number>>
}

export const useMacTable = (
  year: number,
  macData: MacFossilFuel[],
  onVolumeChange: (
    fuel: string,
    month: number,
    volume: number | undefined
  ) => void
) => {
  const { t } = useTranslation()

  const fuels = Array.from(new Set(macData.map((mac) => mac.fuel)))

  const rows = Array.from({ length: 12 }, (_, index) => {
    const month = index + 1
    const monthDate = new Date(year, month - 1, 1)

    const volumes = macData
      .filter((mac) => mac.month === month && mac.year === year)
      .reduce<MacTableRow["volumes"]>((volumes, mac) => {
        volumes[mac.fuel] = mac.volume
        return volumes
      }, {})

    return {
      month,
      monthLabel: formatDate(monthDate, "MMMM"),
      volumes,
    }
  })

  const columns: Column<MacTableRow>[] = [
    {
      header: t("Mois"),
      cell: (row) => row.monthLabel,
      className: css.monthColumn,
    },
    ...fuels.map<Column<MacTableRow>>((fuel) => ({
      header: fuel,
      className: css.fuelColumn,
      cell: (row) => (
        <NumberInput
          label=""
          min={0}
          value={row.volumes[fuel]}
          onChange={(volume) => onVolumeChange(fuel, row.month, volume)}
        />
      ),
    })),
  ]

  return {
    columns,
    rows,
  }
}
