import React from "react";
import cl from "clsx";
import { DOMProps } from "./types";
import { useEntry } from "./registry";
import { useSingleChoice } from "./single-choice";

export type OptionProps<T> = DOMProps<HTMLDivElement, { value: T }>;

export function Option<T>({
  domRef,
  value,
  className,
  ...props
}: OptionProps<T>) {
  const entry = useEntry(value, props.children, domRef);
  const options = useSingleChoice<T>();

  return (
    <div
      {...props}
      ref={entry.ref}
      className={cl("option", { selected: value === options.value }, className)}
      onMouseDown={(e) => {
        e.preventDefault();
        props.onMouseDown?.(e);
      }}
      onClick={(e) => {
        options.onChange(value);
        props.onClick?.(e);
      }}
    />
  );
}

export default Option;
