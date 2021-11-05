import cl from "clsx";
import css from "./scaffold.module.css";

// top bar for the whole website, horizontal flow
export const Header = (props: JSX.IntrinsicElements["header"]) => (
  <header {...props} className={cl(css.header, props.className)} />
);

// main content of the current page, vertical flow, can have a <header> and many <section>
export const Main = (props: JSX.IntrinsicElements["main"]) => (
  <main {...props} className={cl(css.main, props.className)} />
);

// bottom footer with links and info, divided into some vertical <section>
export const Footer = (props: JSX.IntrinsicElements["footer"]) => (
  <footer {...props} className={cl(css.footer, props.className)} />
);

// a special bar to put inside a Main to differentiate it from the rest of the content
export const Bar = (props: JSX.IntrinsicElements["section"]) => (
  <section {...props} className={cl(css.bar, props.className)} />
);

// a enclosed box with its own <header>, many <section> and <footer>
export const Panel = (props: JSX.IntrinsicElements["article"]) => (
  <article {...props} className={cl(css.panel, props.className)} />
);

// a container that automatically arranges its content into a grid
export const Grid = (props: JSX.IntrinsicElements["div"]) => (
  <div {...props} className={cl(css.grid, props.className)} />
);

// a div with vertical flow
export const Column = (props: JSX.IntrinsicElements["div"] & Layout) => (
  <div {...props} {...layout(props)} className={cl(css.column, props.className)} />
); // prettier-ignore

// a div with horizontal flow
export const Row = (props: JSX.IntrinsicElements["div"] & Layout) => (
  <div {...props} {...layout(props)} className={cl(css.row, props.className)} />
);

export interface Layout {
  aside?: boolean;
  spread?: boolean;
}

export function layout(props: Layout) {
  return {
    "data-aside": props.aside ? true : undefined,
    "data-spread": props.spread ? true : undefined,
  };
}
