import { Column } from "common/components/table2"
import { formatDate, formatNumber } from "common/utils/formatters"
import { Dispatch, SetStateAction, useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import { MacFossilFuel } from "../../api"
import { FossilFuel } from "../../types"
import css from "./mac-dialog.module.css"
import { MacInput } from "./mac-input"

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
  fossilFuels: FossilFuel[],
  setMacData: Dispatch<SetStateAction<MacFossilFuel[]>>,
  readOnly?: boolean
) => {
  const { t } = useTranslation()

  const fuelLabels = Object.fromEntries(
    fossilFuels.map((fuel) => [fuel.nomenclature, fuel.label])
  )

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

      if (volume === undefined || isNaN(volume)) {
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
      header: t("{{fuel}} (L)", { fuel: fuelLabels[fuel] ?? fuel }),
      className: css.fuelColumn,
      cell: (row) =>
        row.isTotal || readOnly ? (
          <strong>
            {row.volumes[fuel] !== undefined
              ? formatNumber(row.volumes[fuel])
              : "-"}
          </strong>
        ) : (
          <MacInput
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

type MacDialogDraft = {
  macData: MacFossilFuel[]
  fuels: string[]
}

function getMacDraftKey(entityId: number, year: number) {
  return `mac-fossil-fuels:${entityId}:${year}`
}

function getFuels(macData: MacFossilFuel[]) {
  return Array.from(new Set(macData.map((mac) => mac.fuel)))
}

function getMacDraft(key: string): MacDialogDraft | undefined {
  try {
    const draft = sessionStorage.getItem(key)
    return draft ? JSON.parse(draft) : undefined
  } catch {
    return undefined
  }
}

function saveMacDraft(key: string, draft: MacDialogDraft) {
  sessionStorage.setItem(key, JSON.stringify(draft))
}

function clearMacDraft(key: string) {
  sessionStorage.removeItem(key)
}

export const useMacDialogDraft = (
  entityId: number,
  year: number,
  loadedMacData: MacFossilFuel[] | undefined,
  readOnly?: boolean
) => {
  const [macData, setMacData] = useState<MacFossilFuel[]>([])
  const [fuels, setFuels] = useState<string[]>([])
  const [hasLocalDraft, setHasLocalDraft] = useState(false)
  const draftKey = getMacDraftKey(entityId, year)

  useEffect(() => {
    if (loadedMacData) {
      const draft = readOnly ? undefined : getMacDraft(draftKey)

      setMacData(draft?.macData ?? loadedMacData)
      setFuels(draft?.fuels ?? getFuels(loadedMacData))
      setHasLocalDraft(!!draft)
    }
  }, [draftKey, loadedMacData, readOnly])

  const saveDraft = (draft: MacDialogDraft) => {
    if (!readOnly) {
      saveMacDraft(draftKey, draft)
      setHasLocalDraft(true)
    }
  }

  const setMacDataAndDraft: Dispatch<SetStateAction<MacFossilFuel[]>> = (
    value
  ) => {
    setMacData((currentMacData) => {
      const nextMacData =
        typeof value === "function" ? value(currentMacData) : value

      saveDraft({ macData: nextMacData, fuels })
      return nextMacData
    })
  }

  const addFuels = (fuelsToAdd: string[]) => {
    setFuels((currentFuels) => {
      const nextFuels = Array.from(new Set([...currentFuels, ...fuelsToAdd]))

      saveDraft({ macData, fuels: nextFuels })
      return nextFuels
    })
  }

  const clearDraft = () => {
    clearMacDraft(draftKey)
    setHasLocalDraft(false)
  }

  return {
    macData,
    fuels,
    setMacData: setMacDataAndDraft,
    addFuels,
    clearDraft,
    hasLocalDraft,
  }
}
