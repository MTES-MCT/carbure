import { NavLink, useLocation } from "react-router-dom"
import { layout, Layout } from "../scaffold"
import { useMatcher } from "./tabs.hooks"
import { useEffect, useState } from "react"
import cl from "clsx"
import css from "./tabs.module.css"
import { Text } from "../text"
import { IconName, Icon } from "../icon"

export type TabVariant = "header"

export interface Tab<T extends string> {
  key: T
  label: React.ReactNode
  icon?: IconName
  iconActive?: IconName
  path?: string
  count?: number
}

export interface TabsProps<T extends string> extends Layout {
  className?: string
  style?: React.CSSProperties
  keepSearch?: boolean
  tabs: Tab<T>[]
  focus?: T
  onFocus?: (tab: T) => void
  sticky?: boolean
  // children?: (tab: string) => React.ReactNode
}
export const Tabs = <T extends string>({
  className,
  style,
  keepSearch,
  tabs: tabsConfig,
  focus: controlledFocus,
  onFocus,
  sticky,
  ...props
}: TabsProps<T>) => {
  const matcher = useMatcher()
  const location = useLocation()
  const tabs = tabsConfig.filter(Boolean)
  const match = tabs.find((tab) => matcher(tab.path)) ?? tabs[0]!
  const [focus, setFocus] = useState(controlledFocus ?? match?.key)

  useEffect(() => {
    setFocus(controlledFocus ?? match?.key)
  }, [controlledFocus, match?.key])

  return (
    <nav
      {...layout(props)}
      className={cl(css.tabs, className, sticky && css.sticky)}
      style={style}
    >
      {tabs.map((tab) => {
        const props = {
          className: cl(
            css.tab,
            tab.key === focus && css.active,
            tab.icon && css.icon
          ),
          onClick: () => {
            setFocus(tab.key)
            onFocus?.(tab.key)
          },
        }

        // basic tab that doesn't deal with router
        if (!tab.path) {
          return (
            <Text is="button" fontWeight="bold" {...props} key={tab.key}>
              {renderTabContent(tab, focus)}
            </Text>
          )
        }

        if (tab.path.startsWith("#")) {
          return (
            <Text
              is="a"
              componentProps={{ href: tab.path }}
              fontWeight="bold"
              {...props}
              key={tab.key}
            >
              {renderTabContent(tab, focus)}
            </Text>
          )
        }

        return (
          <Text
            is={NavLink}
            componentProps={{
              to: keepSearch ? `${tab.path}${location.search}` : tab.path,
            }}
            fontWeight="bold"
            {...props}
            key={tab.key}
          >
            {renderTabContent(tab, focus)}
          </Text>
        )
      })}
    </nav>
  )
}

function renderTabContent<T extends string>(tab: Tab<T>, focus: T) {
  return (
    <>
      {((tab.icon && tab.key !== focus) || (!tab.iconActive && tab.icon)) && (
        <Icon size="sm" name={tab.icon} />
      )}
      {tab.iconActive && tab.key === focus && (
        <Icon size="sm" name={tab.iconActive} />
      )}
      {tab.label}
      {tab.count !== undefined && <> ({tab.count})</>}
    </>
  )
}
