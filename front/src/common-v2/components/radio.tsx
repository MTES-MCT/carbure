import cl from "clsx"
import { Disk } from "common-v2/components/icons"
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
  name?: string
  label?: string
}

export interface RadioProps extends RadioControl {
  children?: React.ReactNode
  value?: string | number
  checked?: boolean
  onChange: (value: string) => void
}

export const Radio = ({
  className,
  style,
  children,
  disabled,
  readOnly,
  required,
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
  >
    <input
      hidden
      type="radio"
      disabled={disabled}
      readOnly={readOnly}
      required={required}
      name={name}
      value={value ?? ""}
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
  onChange: (value: V | undefined) => void
  normalize?: Normalizer<T, V>
}

export function RadioGroup<T, V extends string | number>({
  className,
  options,
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
      {normOptions.map(({ value, label }) => (
        <Radio
          key={value}
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
