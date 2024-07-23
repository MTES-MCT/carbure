import Select from "common/components/select"
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
		for (let currentYear = year; currentYear <= year + 1; currentYear++) {
			let currentMonth = currentYear === year ? month : 1
			for (; currentMonth <= 12; currentMonth++) {
				const period = currentYear * 100 + currentMonth
				const date = formatPeriod(period) + "-01"
				const periodString = formatDate(date, "MMMM yyyy")

				list.push({
					value: period,
					label: capitalize(periodString),
				})
			}
		}
		setPeriodList(list)
	}, [])

	return (
		<Select
			placeholder={t("Choisissez une année")}
			value={period}
			onChange={(period) => setPeriod(period!)}
			options={periodList}
		/>
	)
}
