import Button from "common/components/button"
import { NumberInput } from "common/components/inputs2"
import { formatNumber } from "common/utils/formatters"
import { useTranslation } from "react-i18next"

interface VolumeInputProps {
  remainingVolume: number
  onSetMaximumVolume: () => void
}

export const VolumeInput = ({
  onSetMaximumVolume,
  remainingVolume,
  ...props
}: VolumeInputProps) => {
  const { t } = useTranslation()

  return (
    <NumberInput
      required
      label={t("Volume ({{volume}} litres disponibles)", {
        count: remainingVolume,
        volume: formatNumber(remainingVolume),
      })}
      max={remainingVolume}
      min={0}
      step={0.01}
      {...props}
      addon={
        <Button
          label={t("Maximum")}
          action={onSetMaximumVolume}
          variant="primary"
        />
      }
    />
  )
}
