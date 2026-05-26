import { NumberInput } from "common/components/inputs2"
import { Column } from "common/components/table2"
import { formatDate, formatNumber } from "common/utils/formatters"
import { Dispatch, SetStateAction } from "react"
import { useTranslation } from "react-i18next"
import { MacFossilFuel } from "../../api"
import css from "./mac-dialog.module.css"

type MacTableRow = {
  monthLabel: string
  volumes: Partial<Record<string, number>>
} & (
  | {
      month: number
      isTotal?: false
    }
  | {
      month?: undefined
      isTotal: true
    }
)

export const useMacTable = (
  year: number,
  macData: MacFossilFuel[],
  fuels: string[],
  setMacData: Dispatch<SetStateAction<MacFossilFuel[]>>,
  readOnly?: boolean
) => {
  const { t } = useTranslation()

  const updateVolume = (
    fuel: string,
    month: number,
    volume: number | undefined
  ) => {
    setMacData((macData) => {
      const existingMacData = macData.filter(
        (mac) =>
          !(mac.fuel === fuel && mac.year === year && mac.month === month)
      )

      if (volume === undefined) {
        return existingMacData
      }

      return [...existingMacData, { fuel, volume, year, month }]
    })
  }

  const monthlyRows = Array.from({ length: 12 }, (_, index) => {
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

  const totalVolumes = fuels.reduce<MacTableRow["volumes"]>((volumes, fuel) => {
    volumes[fuel] = monthlyRows.reduce(
      (sum, row) => sum + (row.volumes[fuel] ?? 0),
      0
    )
    return volumes
  }, {})

  const rows: MacTableRow[] = [
    ...monthlyRows,
    {
      month: undefined,
      monthLabel: t("Total"),
      volumes: totalVolumes,
      isTotal: true,
    },
  ]

  const columns: Column<MacTableRow>[] = [
    {
      header: t("Mois"),
      cell: (row) =>
        row.isTotal ? <strong>{row.monthLabel}</strong> : row.monthLabel,
      className: css.monthColumn,
    },
    ...fuels.map<Column<MacTableRow>>((fuel) => ({
      header: fuel,
      className: css.fuelColumn,
      cell: (row) =>
        row.isTotal ? (
          <strong>{formatNumber(row.volumes[fuel] ?? 0)}</strong>
        ) : (
          <NumberInput
            readOnly={readOnly}
            label=""
            min={0}
            value={row.volumes[fuel]}
            onChange={(volume) => updateVolume(fuel, row.month, volume)}
          />
        ),
    })),
  ]

  return {
    columns,
    rows,
  }
}
