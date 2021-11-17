import cl from "clsx"
import { Check } from "./icons"
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
      hidden
      type="checkbox"
      disabled={disabled}
      readOnly={readOnly}
      required={required}
      name={name}
      checked={value ?? false}
      className="checkbox-input"
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
  onChange: (value: V[] | undefined) => void
  normalize?: Normalizer<T, V>
}

export function CheckboxGroup<T, V extends string | number>({
  className,
  options,
  disabled,
  readOnly,
  required,
  value,
  onChange,
  normalize = defaultNormalizer,
  ...props
}: CheckboxGroupProps<T, V>) {
  const selection = multipleSelection(value, onChange)
  const normOptions = normalizeItems(options, normalize)

  return (
    <GroupField {...props}>
      {normOptions.map(({ value, label }) => (
        <Checkbox
          key={String(value)}
          name={String(value)}
          label={label}
          disabled={disabled}
          readOnly={readOnly}
          required={required}
          value={selection.isSelected(value)}
          onChange={() => selection.onSelect(value)}
        />
      ))}
    </GroupField>
  )
}

export default Checkbox
