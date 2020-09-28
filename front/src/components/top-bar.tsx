import React from "react"
import { NavLink, Link } from "react-router-dom"

import { ApiState } from "../hooks/use-api"
import { EntitySelection } from "../hooks/use-app"
import { Settings } from "../services/types"

import styles from "./top-bar.module.css"

import Menu from "./dropdown/menu"
import Logo from "./logo"

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

type UserMenuProps = {
  settings: ApiState<Settings>
  entity: EntitySelection
}

const UserMenu = ({ settings, entity }: UserMenuProps) => {
  if (!settings.data) return null

  return (
    <Menu className={styles.userMenu} label={entity.selected?.name ?? "Menu"}>
      <Menu.Group label="Organisations">
        {settings.data.rights.map((right) => (
          <Menu.Item
            key={right.entity.id}
            onClick={() => entity.selectEntity(right.entity)}
          >
            {right.entity.name}
          </Menu.Item>
        ))}
      </Menu.Group>

      <Menu.Group label="Utilisateur">
        <Menu.Item>{settings.data.email}</Menu.Item>
        <Menu.Item>
          <Link to="/settings">Paramètres</Link>
        </Menu.Item>
        <Menu.Item>
          <Link to="/logout">Se déconnecter</Link>
        </Menu.Item>
      </Menu.Group>
    </Menu>
  )
}

type TopbarProps = {
  settings: ApiState<Settings>
  entity: EntitySelection
}

const Topbar = ({ settings, entity }: TopbarProps) => (
  <div className={styles.topBar}>
    <Logo />

    <nav className={styles.pageNav}>
      <PageLink to="/stocks">Stocks</PageLink>
      <PageLink to="/transactions">Transactions</PageLink>
      <PageLink to="/controls">Contrôles</PageLink>
      <PageLink to="/directory">Annuaire</PageLink>
    </nav>

    <UserMenu settings={settings} entity={entity} />
  </div>
)

export default Topbar
