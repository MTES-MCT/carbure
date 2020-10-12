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

  return (to: string) => history.push(pt.join(match.url, to))
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

export const Switch = ({ children }: SwitchProps) => (
  <BaseSwitch>
    {React.Children.map(children, (child: any) =>
      child?.props?.relative ? child.type(child.props) : child
    )}
  </BaseSwitch>
)
