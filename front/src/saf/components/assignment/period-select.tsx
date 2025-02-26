import { Autocomplete } from "common/components/autocomplete2"
import { capitalize, formatDate, formatPeriod } from "common/utils/formatters"
import { Option } from "common/utils/normalize"
import { useEffect, useState } from "react"
import { useTranslation } from "react-i18next"

interface PeriodSelectProps {
  deliveryPeriod: number
  onChange: (value: number) => void
}

export const PeriodSelect = ({
  deliveryPeriod,
  onChange,
}: PeriodSelectProps) => {
  const { t } = useTranslation()
  const [periodList, setPeriodList] = useState<Option<number>[]>()
  const [period, _setPeriod] = useState<number>(deliveryPeriod)

  const setPeriod = (period: number) => {
    _setPeriod(period)
    onChange(period)
  }

  useEffect(() => {
    const month: number = deliveryPeriod % 100
    const year: number = Math.floor(deliveryPeriod / 100)
    const list: Option<number>[] = []
    const currentDate = new Date()
    const currentYear = currentDate.getFullYear()
    const currentMonth = currentDate.getMonth() + 1

    for (let y = year; y <= currentYear; y++) {
      let m = y === year ? month : 1
      for (; m <= 12; m++) {
        if (y === currentYear && m > currentMonth) break
        const period = y * 100 + m
        const date = formatPeriod(period) + "-01"
        const periodString = formatDate(date, "MMMM yyyy")

        list.push({
          value: period,
          label: capitalize(periodString),
        })
      }
    }
    setPeriodList(list)

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <Autocomplete
      label={t("Période d'affectation")}
      placeholder={t("Choisissez une année")}
      value={period}
      onChange={(period) => setPeriod(period!)}
      options={periodList}
    />
  )
}
