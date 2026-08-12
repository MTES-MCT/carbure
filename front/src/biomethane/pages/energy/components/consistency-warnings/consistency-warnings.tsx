import { useTranslation } from "react-i18next"
import { BiomethaneEnergy } from "../../types"
import { Alert } from "common/components/alert2"
import { useState } from "react"

const getSeverity = (
  level?: string
): "info" | "success" | "warning" | "error" => {
  const validLevels = ["info", "success", "warning", "error"]

  if (level && validLevels.includes(level)) {
    return level as "info" | "success" | "warning" | "error"
  }

  return "info"
}

export function ConsistencyWarnings({ energy }: { energy?: BiomethaneEnergy }) {
  const [hiddenIndexes, setHiddenIndexes] = useState<number[]>([])

  const handleClose = (index: number) => {
    setHiddenIndexes((prev) => [...prev, index])
  }

  const { t } = useTranslation("errors")

  const warnings = energy?.consistency_warnings

  if (!warnings || warnings.length === 0) return null

  return (
    <div>
      {warnings.map((warning, index) => {
        if (hiddenIndexes.includes(index)) {
          return null
        }
        return (
          <Alert
            key={`${warning.code}-${index}`}
            severity={getSeverity(warning.level)}
            description={t(warning.code ?? "", {
              defaultValue: warning.message ?? "",
            })}
            small
            closable
            onClose={() => {
              handleClose(index)
            }}
          />
        )
      })}
    </div>
  )
}
