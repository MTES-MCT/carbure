import { ReactNode, useEffect, useState } from "react"
import cl from "clsx"
import {
  NavLink,
  resolvePath,
  useLocation,
  useResolvedPath,
} from "react-router-dom"
import css from "./tabs.module.css"
import { Layout, layout } from "./scaffold"
import { Loader } from "./icons"

export type TabVariant = "header" | "main" | "section" | "sticky" | "switcher"

export interface Tab {
  key: string
  label: React.ReactNode
  path?: string
}

export interface TabsProps extends Layout {
  className?: string
  style?: React.CSSProperties
  variant?: TabVariant
  keepSearch?: boolean
  tabs: Tab[]
  focus?: string
  onFocus?: (tab: string) => void
  children?: (tab: string) => React.ReactNode
}

export const Tabs = ({
  className,
  style,
  variant = "section",
  keepSearch,
  tabs: tabsConfig,
  focus: controlledFocus,
  onFocus,
  children,
  ...props
}: TabsProps) => {
  const matcher = useMatcher()
  const location = useLocation()
  const tabs = tabsConfig.filter(Boolean) as Tab[]
  const match = tabs.find((tab) => matcher(tab.path)) ?? tabs[0]
  const [focus, setFocus] = useState(controlledFocus ?? match?.key)

  useEffect(() => {
    setFocus(controlledFocus ?? match?.key)
  }, [controlledFocus, match?.key])

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

          // anchor link to same page
          if (tab.path.startsWith("#")) {
            return (
              <a {...props} href={tab.path}>
                {tab.label}
              </a>
            )
          }

          return (
            <NavLink
              {...props}
              to={keepSearch ? tab.path + location.search : tab.path}
            >
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
  const location = useLocation()
  const parentPath = useResolvedPath(".").pathname.trim()
  const currentPath = location.pathname.trim()

  return (path: string | undefined) => {
    if (path === undefined) {
      return null
    } else if (path.startsWith("#")) {
      return path === location.hash
    } else {
      const tabPath = resolvePath(path, parentPath).pathname.trim()
      const startsWithPath =
        currentPath.startsWith(tabPath) &&
        currentPath.charAt(tabPath.length) === "/"
      return currentPath === tabPath || startsWithPath
    }
  }
}

interface TabItemProps {
  title: ReactNode
  subtitle: ReactNode
  loading?: boolean
}
/**
 * Default renderer for tab, with a title and a subtitle
 */
export const TabItem = ({ title, subtitle, loading = false }: TabItemProps) => {
  return (
    <div>
      <p
        style={{
          fontWeight: "normal",
        }}
      >
        {loading ? <Loader size={20} /> : subtitle}
      </p>
      <strong>{title}</strong>
    </div>
  )
}

export default Tabs
