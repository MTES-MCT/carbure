import { useTranslation } from "react-i18next"
import { OperationText } from "../operation-text"
import { ceilNumber, floorNumber } from "common/utils/formatters"

type RecapGHGRangeProps = {
  min: number | undefined
  max: number | undefined
}

export function RecapGHGRange({ min, max }: RecapGHGRangeProps) {
  const { t } = useTranslation()

  return (
    <OperationText
      title={t("Réd. GES")}
      description={
        min && max ? `${floorNumber(min, 0)} - ${ceilNumber(max, 0)}%` : ""
      }
    />
  )
}
