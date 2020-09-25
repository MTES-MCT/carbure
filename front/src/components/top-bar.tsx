import React from "react"
import { NavLink, Link } from "react-router-dom"

import { ApiState } from "../hooks/use-api"
import { Entity, Settings } from "../services/settings"

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
  entity: Entity | null
  setEntity: (entity: Entity) => void
}

const UserMenu = ({ settings, entity, setEntity }: UserMenuProps) => {
  if (!settings.data) return null

  return (
    <Menu
      className={styles.userMenu}
      label={entity?.name ?? settings.data.email}
    >
      <Menu.Group label="Organisations">
        {settings.data.rights.map(({ entity }) => (
          <Menu.Item key={entity.id} onClick={() => setEntity(entity)}>
            {entity.name}
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
  entity: Entity | null
  setEntity: (entity: Entity) => void
}

const Topbar = ({ settings, entity, setEntity }: TopbarProps) => (
  <div className={styles.topBar}>
    <Logo />

    <nav className={styles.pageNav}>
      <PageLink to="/stocks">Stocks</PageLink>
      <PageLink to="/transactions">Transactions</PageLink>
      <PageLink to="/controls">Contrôles</PageLink>
      <PageLink to="/directory">Annuaire</PageLink>
    </nav>

    <UserMenu settings={settings} entity={entity} setEntity={setEntity} />
  </div>
)

export default Topbar
