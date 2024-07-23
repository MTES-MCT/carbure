import { useRef, useState } from "react"
import { useAsyncList } from "../hooks/async-list"
import { defaultNormalizer, Normalizer, Sorter } from "../utils/normalize"
import Dropdown, { Trigger } from "./dropdown"
import { ChevronDown } from "./icons"
import { Control, Input } from "./input"
import List from "./list"
import Checkbox from "./checkbox"

export interface MultiSelectProps<T, V = T> extends Control, Trigger {
	clear?: boolean
	search?: boolean
	value?: V[] | undefined
	placeholder?: string
	options?: T[]
	getOptions?: () => Promise<T[]>
	onChange?: (value: V[] | undefined) => void
	normalize?: Normalizer<T, V>
	sort?: Sorter<T, V>
}

export function MultiSelect<T, V>({
	clear,
	search,
	loading,
	value,
	placeholder = "Select options",
	options,
	getOptions,
	onChange,
	onOpen,
	onClose,
	anchor,
	normalize = defaultNormalizer,
	sort,
	...props
}: MultiSelectProps<T, V>) {
	const triggerRef = useRef<HTMLInputElement>(null)
	const [open, setOpen] = useState(false)

	const asyncOptions = useAsyncList({
		selectedValues: value,
		items: options,
		getItems: getOptions,
		normalize,
	})

	function onClear() {
		onChange?.(undefined)
		setOpen(false)
	}

	return (
		<>
			<Input
				{...props}
				domRef={triggerRef}
				loading={loading || asyncOptions.loading}
				type="button"
				value={asyncOptions.label || placeholder}
				icon={<ChevronDown passthrough />}
				onClear={clear && value && value.length > 0 ? onClear : undefined}
			/>

			{!props.disabled && !props.readOnly && (
				<Dropdown
					open={open && asyncOptions.items.length > 0}
					triggerRef={triggerRef}
					onClose={onClose}
					onToggle={setOpen}
					anchor={anchor}
					onOpen={() => {
						onOpen?.()
						asyncOptions.execute()
					}}
				>
					<List
						multiple
						search={search}
						controlRef={triggerRef}
						items={asyncOptions.items}
						selectedValues={value}
						onSelectValues={onChange}
						normalize={normalize}
						sort={sort}
					>
						{({ selected, label }) => (
							<Checkbox readOnly value={selected}>
								{label}
							</Checkbox>
						)}
					</List>
				</Dropdown>
			)}
		</>
	)
}

export default MultiSelect
