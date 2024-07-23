import React from "react"
import cl from "clsx"
import {
	defaultNormalizer,
	Normalizer,
	normalizeItems,
} from "../utils/normalize"
import { multipleSelection } from "../utils/selection"
import Button from "./button"
import { Cross } from "./icons"
import css from "./tag.module.css"

export type TagVariant = "info" | "success" | "warning" | "danger" | "none"

export interface TagProps {
	big?: boolean
	small?: boolean
	variant?: TagVariant
	label?: string
	children?: React.ReactNode
	style?: React.CSSProperties
	className?: string
	onClick?: () => void
	onDismiss?: () => void
}

export const Tag = ({
	big,
	small,
	variant,
	label,
	children,
	className,
	style,
	onClick,
	onDismiss,
}: TagProps) => (
	<span
		style={style}
		className={cl(
			css.tag,
			variant && css[variant],
			big && css.big,
			small && css.small,
			className
		)}
		onClick={onClick}
	>
		{label ?? children}
		{onDismiss && (
			<Button captive variant="icon" icon={Cross} action={onDismiss} />
		)}
	</span>
)

export interface TagGroupProps<T, V> {
	readOnly?: boolean
	children?: React.ReactNode
	variant?: TagVariant
	items: T[] | undefined
	onDismiss?: (value: V[]) => void
	normalize?: Normalizer<T, V>
}

export function TagGroup<T, V>({
	readOnly,
	children,
	variant,
	items,
	onDismiss,
	normalize = defaultNormalizer,
}: TagGroupProps<T, V>) {
	const normItems = normalizeItems(items, normalize)
	const values = normItems.map((item) => item.value)
	const { onSelect } = multipleSelection(values, onDismiss)

	return (
		<div className={css.group}>
			{normItems.map((item) => (
				<Tag
					key={String(item.label)}
					variant={variant}
					label={item.label}
					onDismiss={
						!readOnly && onDismiss ? () => onSelect(item.value) : undefined
					}
				/>
			))}
			{children}
		</div>
	)
}

export default Tag
