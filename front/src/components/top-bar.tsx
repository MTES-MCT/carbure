import React from "react"
import { useLocation } from "react-router-dom"

import { ApiState } from "../hooks/helpers/use-api"
import { EntitySelection } from "../hooks/helpers/use-entity"
import { Settings } from "../services/types"

import styles from "./top-bar.module.css"

import logoMarianne from "../assets/images/logo-marianne.svg"
import logoBetaGouv from "../assets/images/betagouvfr.svg"

import Menu from "./system/menu"
import { Link, NavLink } from "./relative-route"

const Logo = () => (
  <Link to="/" className={styles.logo}>
    <img src={logoMarianne} alt="marianne logo" className={styles.marianne} />
    <span className={styles.carbure}>carbure.</span>
    <img
      src={logoBetaGouv}
      alt="beta.gouv.fr logo"
      className={styles.betagouv}
    />
  </Link>
)

type PageLinkProps = {
  to: string
  children: React.ReactNode
}

const PageLink = ({ to, children }: PageLinkProps) => (
  <NavLink
    relative
    to={to}
    className={styles.pageLink}
    activeClassName={styles.activePageLink}
  >
    {children}
  </NavLink>
)

function changeOrg(path: string, entity: number) {
  return path.replace(/org\/[0-9]+/, `org/${entity}`)
}

type UserMenuProps = {
  settings: ApiState<Settings>
  entity: EntitySelection
}

const UserMenu = ({ settings, entity }: UserMenuProps) => {
  const location = useLocation()

  return (
    <Menu className={styles.userMenu} label={entity?.name ?? "Menu"}>
      <Menu.Group label="Organisations">
        {settings.data?.rights.map((right) => (
          <Menu.Item
            key={right.entity.id}
            to={changeOrg(location.pathname, right.entity.id)}
          >
            {right.entity.name}
          </Menu.Item>
        ))}
      </Menu.Group>

      <Menu.Group label={settings.data?.email ?? "Utilisateur"}>
        <Menu.Item to="/account">Mon compte</Menu.Item>
        <Menu.Item to="/logout">Se déconnecter</Menu.Item>
      </Menu.Group>
    </Menu>
  )
}

function canTrade(entity: EntitySelection) {
  return entity && (entity.has_trading || entity.entity_type === "Trader")
}

function isAdmin(entity: EntitySelection) {
  return entity && entity.entity_type === "Administration"
}

type TopbarProps = {
  entity: EntitySelection
  settings: ApiState<Settings>
}

const Topbar = ({ entity, settings }: TopbarProps) => (
  <header className={styles.topBar}>
    <Logo />

    <nav className={styles.pageNav}>
      {canTrade(entity) && <PageLink to="stocks">Stocks</PageLink>}
      <PageLink to="transactions">Transactions</PageLink>
      {isAdmin(entity) && (
        <PageLink to="administration">Administration</PageLink>
      )}
      <PageLink to="settings">Société</PageLink>
    </nav>

    <UserMenu settings={settings} entity={entity} />
  </header>
)

export default Topbar
