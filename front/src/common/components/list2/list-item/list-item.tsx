import cl from "clsx"
import { CheckLine } from "common/components/icon"
import { Text } from "common/components/text"
import css from "./list-item.module.css"

export type ListItemProps<V> = {
  label: string
  disabled?: boolean
  level?: number
  selected?: boolean
  focused?: boolean
  onFocus?: (value: V) => void
  onClick?: (value: V) => void
  value: V
  children: React.ReactNode

  // Add a border bottom
  borderBottom?: boolean

  // Add a hover effect
  hoverable?: boolean
}
export const ListItem = <V,>({
  label,
  disabled,
  level = 0,
  selected,
  focused,
  onFocus,
  onClick,
  value,
  children,
  borderBottom,
  hoverable = false,
}: ListItemProps<V>) => {
  return (
    <Text
      is="li"
      key={label}
      data-key={label}
      data-disabled={disabled ? true : undefined}
      data-level={level > 0 ? level : undefined}
      data-selected={selected ? true : undefined}
      data-focused={focused ? true : undefined}
      componentProps={{
        onMouseOver: !disabled ? () => onFocus?.(value) : undefined,
        onClick: !disabled ? () => onClick?.(value) : undefined,
      }}
      size="sm"
      className={cl(
        css["list-item"],
        borderBottom && css["border-bottom"],
        hoverable && css["hoverable"]
      )}
    >
      {children}
      {selected && <CheckLine size="sm" />}
    </Text>
  )
}
