import cl from "clsx"
import { Disk } from "common/components/icons"
import { singleSelection } from "../utils/selection"
import {
	defaultNormalizer,
	Normalizer,
	normalizeItems,
} from "../utils/normalize"
import css from "./radio.module.css"
import { GroupField } from "./input"

export interface RadioControl {
	className?: string
	style?: React.CSSProperties
	disabled?: boolean
	readOnly?: boolean
	required?: boolean
	autoFocus?: boolean
	name?: string
	label?: string
}

export interface RadioProps extends RadioControl {
	children?: React.ReactNode
	value?: string | number
	checked?: boolean
	onChange?: (value: string) => void
}

export const Radio = ({
	className,
	style,
	children,
	disabled,
	readOnly,
	required,
	autoFocus,
	label,
	name,
	value,
	checked,
	onChange,
}: RadioProps) => (
	<label
		data-radio
		data-checked={checked ? true : undefined}
		data-disabled={disabled ? true : undefined}
		className={cl(css.radio, className)}
		style={style}
		onClick={(e) => e.stopPropagation()}
	>
		<input
			type="radio"
			className={css.input}
			disabled={disabled}
			readOnly={readOnly}
			required={required}
			name={name}
			value={value ?? ""}
			autoFocus={autoFocus}
			checked={checked}
			onChange={onChange ? (e) => onChange(e.target.value) : undefined}
			// prevent duplicate click event being propagated when clicking on label
			onClick={(e) => e.stopPropagation()}
		/>
		<div className={css.circle}>{checked && <Disk />}</div>
		{label ?? children}
	</label>
)

export interface RadioGroupProps<T, V> extends RadioControl {
	options: T[]
	value: V | undefined
	onChange?: (value: V | undefined) => void
	normalize?: Normalizer<T, V>
}

export function RadioGroup<T, V extends string | number>({
	className,
	options,
	autoFocus,
	name,
	value,
	onChange,
	normalize = defaultNormalizer,
	...props
}: RadioGroupProps<T, V>) {
	const selection = singleSelection(value, onChange)
	const normOptions = normalizeItems(options, normalize)

	return (
		<GroupField {...props}>
			{normOptions.map(({ value, label }, i) => (
				<Radio
					key={value}
					autoFocus={autoFocus && i === 0}
					disabled={props.disabled}
					readOnly={props.readOnly}
					required={props.required}
					name={name}
					value={value}
					label={label}
					checked={selection.isSelected(value)}
					onChange={() => selection.onSelect(value)}
				/>
			))}
		</GroupField>
	)
}

export default Radio
