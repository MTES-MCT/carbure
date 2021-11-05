import { useEffect, useState } from "react";
import { Link, matchPath, useLocation } from 'react-router-dom'
import cl from "clsx";
import css from "./tabs.module.css";

export type TabVariant = "header" | "main" | "section" | "sticky";

export interface Tab {
  key: string;
  label: React.ReactNode;
  path?: string;
}

export interface TabsProps {
  tabs: Tab[];
  variant?: TabVariant;
  onFocus?: (tab: string) => void;
  children?: (tab: string) => React.ReactNode;
}

export const Tabs = ({ variant = "section", tabs, children }: TabsProps) => {
  const location = useLocation()
  const match = tabs.find(tab => matchPath(tab.path ?? '', location.pathname)) ?? tabs[0]

  const [focus, setFocus] = useState(match.key);

  useEffect(() => {
    setFocus(match.key);
  }, [match.key]);

  return (
    <>
      <nav className={cl(css.tabs, css[variant])}>
        {tabs.map((tab) => {
          const props = {
            key: tab.key,
            className: cl(tab.key === focus && css.active),
            onClick: () => setFocus(tab.key),
          };

          return tab.path ? (
            <Link {...props} to={tab.path}>
              {tab.label}
            </Link>
          ) : (
            <a {...props}>{tab.label}</a>
          );
        })}
      </nav>

      {children?.(focus)}
    </>
  );
};
