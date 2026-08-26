import { Alert } from "common/components/alert2"
import { ConsistencyWarning } from "biomethane/pages/energy/types"
import { useState } from "react"
import { useTranslation } from "react-i18next"

type ConsistencyWarningsProps = {
  warnings?: ConsistencyWarning[]
}

export function ConsistencyWarnings({ warnings }: ConsistencyWarningsProps) {
  const [hiddenIndexes, setHiddenIndexes] = useState<number[]>([])

  const handleClose = (index: number) => {
    setHiddenIndexes((prev) => [...prev, index])
  }

  const { t } = useTranslation("errors")

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
            severity={warning.level}
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
