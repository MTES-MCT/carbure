import {
  NavLink as RouterNavLink,
  NavLinkProps as RouterNavLinkProps,
} from "react-router-dom"
import cl from "clsx"
import css from "./nav-link.module.css"

export type NavLinkProps = RouterNavLinkProps & {
  underline?: boolean
}

export const NavLink = ({
  children,
  underline,
  className,
  ...props
}: NavLinkProps) => {
  return (
    <RouterNavLink
      {...props}
      className={cl(underline && css.underline, className)}
    >
      {children}
    </RouterNavLink>
  )
}
