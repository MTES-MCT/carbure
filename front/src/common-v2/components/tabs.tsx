import { useEffect, useState } from "react"
import cl from "clsx"
import {
  Link,
  matchPath,
  resolvePath,
  useLocation,
  useResolvedPath,
} from "react-router-dom"
import css from "./tabs.module.css"

export type TabVariant = "header" | "main" | "section" | "sticky"

export interface Tab {
  key: string
  label: React.ReactNode
  path?: string
}

export interface TabsProps {
  tabs: (Tab | false)[]
  variant?: TabVariant
  onFocus?: (tab: string) => void
  children?: (tab: string) => React.ReactNode
}

export const Tabs = ({ variant = "section", tabs, children }: TabsProps) => {
  const matcher = useMatcher()
  const okTabs = tabs.filter(Boolean) as Tab[]
  const match = okTabs.find((tab) => matcher(tab.path)) ?? okTabs[0]

  const [focus, setFocus] = useState(match.key)

  useEffect(() => {
    setFocus(match.key)
  }, [match.key])

  return (
    <>
      <nav className={cl(css.tabs, css[variant])}>
        {okTabs.map((tab) => {
          const props = {
            key: tab.key,
            className: cl(tab.key === focus && css.active),
            onClick: () => setFocus(tab.key),
          }

          return tab.path ? (
            <Link {...props} to={tab.path}>
              {tab.label}
            </Link>
          ) : (
            <a {...props}>{tab.label}</a>
          )
        })}
      </nav>

      {children?.(focus)}
    </>
  )
}

export function useMatcher() {
  const parentPath = useResolvedPath(".").pathname
  const currentPath = useLocation().pathname

  return (path: string | undefined = "") =>
    matchPath(currentPath, resolvePath(path, parentPath).pathname)
}

export default Tabs
