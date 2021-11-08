import React, { useCallback, useContext, useState } from "react";
import cl from "clsx";
import css from "./form.module.css";

export type FormVariant = "inline" | "complex";

export interface FormProps<T> {
  className?: string;
  style?: React.CSSProperties;
  children: React.ReactNode;
  variant?: FormVariant;
  value?: T;
  onChange?: (change: FormChange<T>) => void;
  onSubmit?: (e: React.FormEvent<HTMLFormElement>) => void;
}

export function Form<T>({
  variant,
  value,
  children,
  className,
  onChange = () => {},
  onSubmit,
}: FormProps<T>) {
  const hasContext = value !== undefined && onChange !== undefined;
  const context = hasContext ? { value, onChange } : undefined;

  return (
    <FormContext.Provider value={context}>
      <form
        className={cl(css.form, variant && css[variant], className)}
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit?.(e);
        }}
      >
        {children}
      </form>
    </FormContext.Provider>
  );
}

export interface FieldsetProps {
  className?: string;
  style?: React.CSSProperties;
  children?: React.ReactNode;
  label?: string;
}

export const Fieldset = ({
  label,
  className,
  style,
  children,
}: FieldsetProps) => (
  <fieldset className={cl(css.fieldset, className)} style={style}>
    {label && <legend>{label}</legend>}
    {children}
  </fieldset>
);

export interface FormHook<T> {
  state: T;
  bind: Bind<T>;
  onChange: (change: FormChange<T>) => void;
  setState: React.Dispatch<React.SetStateAction<T>>;
}

export interface FormOptions<T> {
  setValue?: (nextState: T, prevState?: T) => T;
}

export function useForm<T>(
  initialState: T,
  { setValue = (v) => v }: FormOptions<T> = {}
): FormHook<T> {
  const [state, setState] = useState(initialState);

  const onChange = useCallback(
    (change: FormChange<T>) => {
      setState((state) =>
        setValue({ ...state, [change.name]: change.value }, state)
      );
    },
    [setValue]
  );

  const bind = useBindCallback(state, onChange);

  return { state, bind, onChange, setState };
}

export function useBind<T>(): Bind<T> | undefined {
  const form = useContext(FormContext);

  if (form === undefined) {
    throw new Error("useBind can only be used inside a FormContext");
  }

  return useBindCallback<T>(form.value, form.onChange);
}

function useBindCallback<T>(
  value: T,
  onChange: (change: FormChange<T>) => void
): Bind<T> {
  return useCallback(
    (name, option) => {
      return {
        name,
        value: option ?? value[name],
        checked: option ? option === value[name] : undefined,
        onChange: (value) => onChange({ name, value }),
      };
    },
    [value, onChange]
  );
}

export interface FormContextValue<T> {
  value: T;
  onChange: (change: FormChange<T>) => void;
}

export const FormContext = React.createContext<
  FormContextValue<any> | undefined
>(undefined);

export interface FormChange<T> {
  value: T[keyof T] | undefined;
  name: keyof T;
}

export type Bind<T> = <N extends keyof T>(
  name: N,
  option?: T[N]
) => BindProps<T, N>;

export interface BindProps<T, N extends keyof T> {
  name: N;
  value: T[N];
  onChange: (value: T[N]) => void;
  checked?: boolean;
}

export default Form;
