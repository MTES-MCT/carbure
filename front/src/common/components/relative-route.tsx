import React from "react"
import pt from "path"

import {
  Route as BaseRoute,
  Link as BaseLink,
  NavLink as BaseNavLink,
  Redirect as BaseRedirect,
  Switch as BaseSwitch,
  useHistory,
  useRouteMatch,
  RouteProps,
  LinkProps,
  NavLinkProps,
  RedirectProps,
  SwitchProps,
} from "react-router-dom"

export function useRelativePush() {
  const history = useHistory()
  const match = useRouteMatch()

  return (to: string, state?: any) =>
    history.push(pt.join(match.url, to), state)
}

type Relative = {
  relative?: boolean
}

export const Route = ({ path, relative, ...props }: RouteProps & Relative) => {
  const match = useRouteMatch()
  const basePath = relative ? pt.join(match.path, path as string) : path
  return <BaseRoute {...props} path={basePath} />
}

export const Link = ({ to, relative, ...props }: LinkProps & Relative) => {
  const match = useRouteMatch()
  const baseTo = relative ? pt.join(match.url, to as string) : to
  return <BaseLink {...props} to={baseTo} />
}

export const NavLink = ({
  to,
  relative,
  ...props
}: NavLinkProps & Relative) => {
  const match = useRouteMatch()
  const baseTo = relative ? pt.join(match.url, to as string) : to
  return <BaseNavLink {...props} to={baseTo} />
}

export const Redirect = ({
  from,
  to,
  relative,
  ...props
}: RedirectProps & Relative) => {
  const match = useRouteMatch()
  const baseFrom = from && relative ? pt.join(match.url, from) : from
  const baseTo = relative ? pt.join(match.url, to as string) : to
  return <BaseRedirect {...props} from={baseFrom} to={baseTo} />
}

// the basic Switch component from react-router only works with basic react-router Route component
// this component tricks it into working with the custom routing components of this file
export const Switch = ({ children }: SwitchProps) => {
  const match = useRouteMatch()

  return (
    <BaseSwitch>
      {React.Children.map(children, (child: any) => {
        // not relative child, return as is
        if (!child?.props?.relative) {
          return child
        }
        // relative route child, create equivalent base route
        else if (child.type === Route) {
          const path = pt.join(match.path, child.props.path)
          return <BaseRoute {...child.props} path={path} />
        }
        // relative redirect child, create equivalent base redirect
        else if (child.type === Redirect && child.props.relative) {
          const from = child.props.from && pt.join(match.url, child.props.from)
          const to = pt.join(match.url, child.props.to)
          return <BaseRedirect {...child.props} from={from} to={to} />
        }
      })}
    </BaseSwitch>
  )
}
