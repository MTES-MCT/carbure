import { NavLink, useLocation } from "react-router-dom"
import { layout, Layout } from "../scaffold"
import { useMatcher } from "./tabs.hooks"
import { useEffect, useState } from "react"
import cl from "clsx"
import css from "./tabs.module.css"
import { Text } from "../text"
import { IconProps } from "../icon"

export type TabVariant = "header"

export interface Tab<T extends string> {
  key: T
  label: React.ReactNode
  icon?: React.ComponentType<IconProps>
  iconActive?: React.ComponentType<IconProps>
  path?: string
}

export interface TabsProps<T extends string> extends Layout {
  className?: string
  style?: React.CSSProperties
  variant?: TabVariant
  keepSearch?: boolean
  tabs: Tab<T>[]
  focus?: T
  onFocus?: (tab: T) => void
  // children?: (tab: string) => React.ReactNode
}
export const Tabs = <T extends string>({
  className,
  style,
  keepSearch,
  tabs: tabsConfig,
  focus: controlledFocus,
  onFocus,
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
    <nav {...layout(props)} className={cl(css.tabs, className)} style={style}>
      {tabs.map(({ icon: Icon, iconActive: IconActive, ...tab }) => {
        const props = {
          className: cl(
            css.tab,
            tab.key === focus && css.active,
            Icon && css.icon
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
              {((Icon && tab.key !== focus) || (!IconActive && Icon)) && (
                <Icon size="sm" />
              )}
              {IconActive && tab.key === focus && <IconActive size="sm" />}
              {tab.label}
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
              {Icon && <Icon size="sm" />}
              {tab.label}
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
            {Icon && <Icon size="sm" />}
            {tab.label}
          </Text>
        )
      })}
    </nav>
  )
}
