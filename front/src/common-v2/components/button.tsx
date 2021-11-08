import cl from "clsx";
import { useState } from "react";
import { Loader } from "./icons";
import css from "./button.module.css";
import { Layout, layout } from "./scaffold";

export type ButtonVariant =
  | "primary"
  | "secondary"
  | "success"
  | "warning"
  | "danger"
  | "text"
  | "link"
  | "icon";

export interface ButtonProps<T = void> extends Layout {
  className?: string;
  style?: React.CSSProperties;
  children?: React.ReactNode;
  domRef?: React.RefObject<HTMLButtonElement>;
  disabled?: boolean;
  loading?: boolean;
  captive?: boolean;
  variant?: ButtonVariant;
  label?: string;
  icon?: React.ReactNode | (() => React.ReactNode);
  submit?: string | boolean;
  tabIndex?: number;
  action?: (() => T) | (() => Promise<T>);
  dialog?: (close: () => void) => React.ReactNode;
  onSuccess?: (result: T) => void;
  onError?: (error: unknown) => void;
}

export function Button<T>({
  className,
  style,
  children,
  domRef,
  disabled,
  loading,
  aside,
  spread,
  captive,
  variant,
  label,
  icon: Icon,
  submit,
  tabIndex,
  action,
  dialog,
  onSuccess,
  onError,
}: ButtonProps<T>) {
  const [active, showDialog] = useState(false);

  const icon = typeof Icon === "function" ? <Icon /> : Icon;
  const hasIconAndText = Boolean(Icon) && Boolean(label || children);

  // prettier-ignore
  const openDialog = dialog
    ? () => showDialog(true)
    : undefined;

  const runAction = action
    ? () => handle(action, { onSuccess, onError })
    : undefined;

  return (
    <>
      <button
        ref={domRef}
        {...layout({ aside, spread })}
        data-captive={captive ? true : undefined}
        tabIndex={tabIndex}
        disabled={disabled || loading}
        type={submit ? "submit" : "button"}
        form={typeof submit === "string" ? submit : undefined}
        style={style}
        onClick={openDialog ?? runAction}
        className={cl(
          css.button,
          variant && css[variant],
          hasIconAndText && css.composite,
          className
        )}
      >
        {loading ? <Loader /> : icon}
        {variant !== "icon" && (label ?? children)}
      </button>

      {active && dialog?.(() => showDialog(false))}
    </>
  );
}

type Action<T = void> = (() => T) | (() => Promise<T>);

interface Handlers<T> {
  onSuccess?: (result: T) => void;
  onError?: (error: unknown) => void;
}

async function handle<T>(action: Action<T>, handlers: Handlers<T>) {
  try {
    const result = await action();
    handlers.onSuccess?.(result);
  } catch (error) {
    handlers.onError?.(error);
  }
}

export default Button;
