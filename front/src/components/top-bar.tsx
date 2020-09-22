import React from "react"
import { NavLink } from "react-router-dom"

import { ApiState } from "../hooks/use-api"
import { Settings } from "../services/settings"

import styles from "./top-bar.module.css"

import { Menu, MenuLink } from "./system"
import Logo from "./logo"

type PageLinkProps = {
  to: string
  children: React.ReactNode
}

type UserMenuProps = {
  settings: ApiState<Settings>
  entity: number
  setEntity: (entity: number) => void
}

type TopbarProps = {
  settings: ApiState<Settings>
  entity: number
  setEntity: (entity: number) => void
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

const UserMenu = ({ settings, entity, setEntity }: UserMenuProps) => {
  if (!settings.data) return null

  function onChange(e: React.ChangeEvent<HTMLSelectElement>) {
    // ignore options with no values
    if (e.target.value) setEntity(parseInt(e.target.value, 10))
  }

  return (
    <Menu className={styles.userMenu} value={entity} onChange={onChange}>
      <optgroup label="Organisation">
        {settings.data.rights.map(({ entity }) => (
          <option key={entity.id} value={entity.id}>
            {entity.name}
          </option>
        ))}
      </optgroup>
      <optgroup label="Utilisateur">
        <option disabled>{settings.data.email}</option>
        <MenuLink to="/settings">Paramètres</MenuLink>
        <MenuLink to="/logout">Se déconnecter</MenuLink>
      </optgroup>
    </Menu>
  )
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
