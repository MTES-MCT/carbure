import React from "react"
import { NavLink } from "react-router-dom"

import styles from "./top-bar.module.css"
import Logo from "./logo"
import { Menu } from "./system"

type PageLinkProps = {
  to: string
  children: React.ReactNode
}

const PageLink = ({ to, children }: PageLinkProps) => (
  <NavLink
    to={to}
    className={styles.pageLink}
    activeClassName={styles.activePageLink}
  >
    {children}
  </NavLink>
)

const UserMenu = () => (
  <Menu
    label="José-Marie-Pierre de Laporte d'Entrée"
    className={styles.userMenu}
  >
    <option>Logout</option>
  </Menu>
)

const Topbar = () => (
  <div className={styles.topBar}>
    <Logo />

    <nav className={styles.pageNav}>
      <PageLink to="/stocks">Stocks</PageLink>
      <PageLink to="/transactions">Transactions</PageLink>
      <PageLink to="/controles">Contrôles</PageLink>
      <PageLink to="/annuaire">Annuaire</PageLink>
    </nav>

    <UserMenu />
  </div>
)

export default Topbar
