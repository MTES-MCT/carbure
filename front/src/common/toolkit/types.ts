import React from "react";

export const noop = () => {};

export type Merge<A, B> = Omit<A, keyof B> & B;

export type DOMProps<H extends HTMLElement, P extends object = {}> = Merge<
  React.HTMLProps<H>,
  P & { domRef?: React.RefObject<H> }
>;

export type ChangeEvent<T = HTMLInputElement> = React.ChangeEvent<T>;
