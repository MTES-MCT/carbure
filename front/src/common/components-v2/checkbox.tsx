import cl from "clsx";
import { Check } from "./icons";
import css from "./checkbox.module.css";
import { GroupField } from "./input";
import { multipleSelection } from "../hooks/selection";
import {
  defaultNormalizer,
  Normalizer,
  normalizeTree,
} from "../hooks/normalize";

export interface CheckboxControl {
  className?: string;
  style?: React.CSSProperties;
  disabled?: boolean;
  readOnly?: boolean;
  required?: boolean;
  name?: string;
  label?: string;
}

export interface CheckboxProps extends CheckboxControl {
  children?: React.ReactNode;
  value: boolean;
  onChange?: (value: boolean) => void;
}

export const Checkbox = ({
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
);

export interface CheckboxGroupProps<T> extends CheckboxControl {
  options: T[];
  value: T[] | undefined;
  onChange: (value: T[] | undefined) => void;
  normalize?: Normalizer<T>;
}

export function CheckboxGroup<T>({
  className,
  options,
  disabled,
  readOnly,
  required,
  value,
  onChange,
  normalize = defaultNormalizer,
  ...props
}: CheckboxGroupProps<T>) {
  const selection = multipleSelection(value, onChange, normalize);
  const normOptions = normalizeTree(options, normalize);

  return (
    <GroupField {...props}>
      {normOptions.map(({ key, value, label }) => (
        <Checkbox
          key={key}
          name={key}
          label={label}
          disabled={disabled}
          readOnly={readOnly}
          required={required}
          value={selection.isSelected(value)}
          onChange={() => selection.onSelect(value)}
        />
      ))}
    </GroupField>
  );
}

export default Checkbox;
