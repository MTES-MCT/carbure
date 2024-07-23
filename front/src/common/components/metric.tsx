import cl from "clsx"
import css from "./metric.module.css"

export interface MetricProps {
	className?: string
	style?: React.CSSProperties
	label: string
	value: number | string
	children?: (metric: string) => React.ReactNode
}

export const Metric = ({ label, value }: MetricProps) => {
	return (
		<div className={cl(css.metric)}>
			<p>
				<strong>{value}</strong>
			</p>
			<p>{label}</p>
		</div>
	)
}

export default Metric
