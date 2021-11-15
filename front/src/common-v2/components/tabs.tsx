import { CSSProperties, useEffect, useState } from "react"
import cl from "clsx"
import {
  Link,
  matchPath,
  resolvePath,
  useLocation,
  useResolvedPath,
} from "react-router-dom"
import css from "./tabs.module.css"
import { Layout, layout } from "./scaffold"

export type TabVariant = "header" | "main" | "section" | "sticky" | "switcher"

export interface Tab {
  key: string
  label: React.ReactNode
  path?: string
}

export interface TabsProps extends Layout {
  className?: string
  style?: CSSProperties
  tabs: (Tab | false)[]
  variant?: TabVariant
  focus?: string
  onFocus?: (tab: string) => void
  children?: (tab: string) => React.ReactNode
}

export const Tabs = ({
  className,
  style,
  variant = "section",
  tabs,
  focus: controlledFocus,
  onFocus,
  children,
  ...props
}: TabsProps) => {
  const matcher = useMatcher()
  const okTabs = tabs.filter(Boolean) as Tab[]
  const match = okTabs.find((tab) => matcher(tab.path)) ?? okTabs[0]

  const [focus, setFocus] = useState(controlledFocus ?? match.key)

  useEffect(() => {
    setFocus(controlledFocus ?? match.key)
  }, [controlledFocus, match.key])

  return (
    <>
      <nav
        {...layout(props)}
        className={cl(css.tabs, css[variant], className)}
        style={style}
      >
        {okTabs.map((tab) => {
          const props = {
            key: tab.key,
            className: cl(tab.key === focus && css.active),
            onClick: () => {
              setFocus(tab.key)
              onFocus?.(tab.key)
            },
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
