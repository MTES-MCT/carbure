import cl from "clsx"
import { Check } from "common/components/icons"
import css from "./checkbox.module.css"
import { GroupField } from "./input"
import { multipleSelection } from "../utils/selection"
import {
  defaultNormalizer,
  Normalizer,
  normalizeItems,
} from "../utils/normalize"

export interface CheckboxControl {
  className?: string
  style?: React.CSSProperties
  disabled?: boolean
  autoFocus?: boolean
  readOnly?: boolean
  required?: boolean
  name?: string
  label?: string
}

export interface CheckboxProps extends CheckboxControl {
  captive?: boolean
  children?: React.ReactNode
  value: boolean
  onChange?: (value: boolean) => void
}

export const Checkbox = ({
  captive,
  disabled,
  readOnly,
  required,
  autoFocus,
  value,
  label,
  name,
  className,
  style,
  children,
  onChange,
}: CheckboxProps) => (
  <label
    data-checkbox
    data-disabled={disabled ? true : undefined}
    data-checked={value ? true : undefined}
    aria-checked={value ? true : undefined}
    onClick={captive ? (e) => e.stopPropagation() : undefined}
    className={cl(css.checkbox, className)}
    style={style}
  >
    <input
      type="checkbox"
      autoFocus={autoFocus}
      disabled={disabled}
      readOnly={readOnly}
      required={required}
      name={name}
      checked={value ?? false}
      className={cl("checkbox-input", css.input)}
      onChange={onChange ? (e) => onChange(e.target.checked) : undefined}
      // prevent duplicate click event being propagated when clicking on label
      onClick={(e) => e.stopPropagation()}
    />
    <div className={css.square}>{value ? <Check stroke={3} /> : null}</div>
    {label ?? children}
  </label>
)

export interface CheckboxGroupProps<T, V> extends CheckboxControl {
  options: T[]
  value: V[] | undefined
  variant?: "default" | "opacity"
  onChange: (value: V[] | undefined) => void
  onToggle?: (value: V, checked: boolean) => void
  normalize?: Normalizer<T, V>
}

export function CheckboxGroup<T, V extends string | number>({
  className,
  variant = "default",
  options,
  disabled,
  readOnly,
  required,
  value,
  onChange,
  onToggle,
  normalize = defaultNormalizer,
  ...props
}: CheckboxGroupProps<T, V>) {
  const selection = multipleSelection(value, onChange)
  const normOptions = normalizeItems(options, normalize)

  return (
    <GroupField {...props} className={cl(className, variant && css[variant])}>
      {normOptions.map(({ value, label }) => (
        <Checkbox
          key={String(value)}
          name={String(value)}
          label={label}
          disabled={disabled}
          readOnly={readOnly}
          required={required}
          value={selection.isSelected(value)}
          onChange={(checked) => {
            selection.onSelect(value)
            onToggle?.(value, checked)
          }}
        />
      ))}
    </GroupField>
  )
}

export default Checkbox
