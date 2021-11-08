import cl from "clsx";
import { Disk } from "./icons";
import { singleSelection } from "../hooks/selection";
import {
  defaultNormalizer,
  Normalizer,
  normalizeTree,
} from "../hooks/normalize";
import css from "./radio.module.css";
import { GroupField } from "./input";

export interface RadioControl {
  className?: string;
  style?: React.CSSProperties;
  disabled?: boolean;
  readOnly?: boolean;
  required?: boolean;
  name?: string;
  label?: string;
}

export interface RadioProps extends RadioControl {
  children?: React.ReactNode;
  value?: string | number;
  checked?: boolean;
  onChange: (value: string) => void;
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
);

export interface RadioGroupProps<T> extends RadioControl {
  options: T[];
  value: T | undefined;
  onChange: (value: T | undefined) => void;
  normalize?: Normalizer<T>;
}

export function RadioGroup<T>({
  className,
  options,
  name,
  value,
  onChange,
  normalize = defaultNormalizer,
  ...props
}: RadioGroupProps<T>) {
  const selection = singleSelection(value, onChange, normalize);
  const normOptions = normalizeTree(options, normalize);

  return (
    <GroupField {...props}>
      {normOptions.map(({ key, value, label }) => (
        <Radio
          key={key}
          disabled={props.disabled}
          readOnly={props.readOnly}
          required={props.required}
          name={name}
          value={key}
          label={label}
          checked={selection.isSelected(value)}
          onChange={() => selection.onSelect(value)}
        />
      ))}
    </GroupField>
  );
}

export default Radio;
