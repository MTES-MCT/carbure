import { NumberInput } from "common/components/inputs2"
import { Column } from "common/components/table2"
import { formatDate } from "common/utils/formatters"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import css from "./mac-dialog.module.css"

type MacData = {
  fuel: string
  volume: number
  year: number
  month: number
}

type MacTableRow = {
  month: number
  monthLabel: string
  volumes: Partial<Record<string, number>>
}

const initialMacData: MacData[] = [
  {
    fuel: "Gazole",
    volume: 1200,
    year: 2026,
    month: 1,
  },
  {
    fuel: "Essence",
    volume: 800,
    year: 2026,
    month: 2,
  },
  {
    fuel: "SP95-E10",
    volume: 650,
    year: 2026,
    month: 3,
  },
  {
    fuel: "E85",
    volume: 420,
    year: 2026,
    month: 4,
  },
  {
    fuel: "B100",
    volume: 300,
    year: 2026,
    month: 5,
  },
  {
    fuel: "GNR",
    volume: 950,
    year: 2026,
    month: 6,
  },
  {
    fuel: "Jet A-1",
    volume: 510,
    year: 2026,
    month: 7,
  },
  {
    fuel: "GPL",
    volume: 260,
    year: 2026,
    month: 8,
  },
  {
    fuel: "HVO",
    volume: 380,
    year: 2026,
    month: 9,
  },
  {
    fuel: "Fioul domestique",
    volume: 740,
    year: 2026,
    month: 10,
  },
]

export const useMacTable = (year: number) => {
  const { t } = useTranslation()
  const [macData, setMacData] = useState(initialMacData)

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

      return [
        ...existingMacData,
        {
          fuel,
          volume,
          year,
          month,
        },
      ]
    })
  }

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
