import { useEffect, useState } from "react"
import cl from "clsx"
import {
  NavLink,
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
  style?: React.CSSProperties
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
  tabs: tabsConfig,
  focus: controlledFocus,
  onFocus,
  children,
  ...props
}: TabsProps) => {
  const matcher = useMatcher()
  const tabs = tabsConfig.filter(Boolean) as Tab[]
  const match = tabs.find((tab) => matcher(tab.path)) ?? tabs[0]
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
        {tabs.map((tab) => {
          const props = {
            key: tab.key,
            className: cl(css.tab, tab.key === focus && css.active),
            onClick: () => {
              setFocus(tab.key)
              onFocus?.(tab.key)
            },
          }

          // basic tab that doesn't deal with router
          if (!tab.path) {
            return <button {...props}>{tab.label}</button>
          }

          return (
            <NavLink {...props} to={tab.path}>
              {tab.label}
            </NavLink>
          )
        })}
      </nav>

      {children?.(focus)}
    </>
  )
}

export function useMatcher() {
  const parentPath = useResolvedPath(".")
  const currentPath = useLocation()

  return (path: string | undefined) => {
    if (path === undefined) {
      return null
    } else if (path.charAt(0) === "#") {
      return currentPath.hash === path
    } else {
      const tabPath = resolvePath(path, parentPath.pathname)
      const startsWithPath =
        currentPath.pathname.startsWith(tabPath.pathname) &&
        currentPath.pathname.charAt(tabPath.pathname.length) === "/"
      return currentPath === tabPath || startsWithPath
    }
  }
}

export default Tabs
