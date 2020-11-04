import React from "react"

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

type UserMenuProps = {
  settings: ApiState<Settings>
  entity: EntitySelection
}

const UserMenu = ({ settings, entity }: UserMenuProps) => (
  <Menu className={styles.userMenu} label={entity?.name ?? "Menu"}>
    <Menu.Group label="Organisations">
      {settings.data?.rights.map((right) => (
        <Menu.Item key={right.entity.id} to={`/org/${right.entity.id}`}>
          {right.entity.name}
        </Menu.Item>
      ))}
    </Menu.Group>

    <Menu.Group label="Utilisateur">
      <Menu.Item>{settings.data?.email}</Menu.Item>
      <Menu.Item to={`/org/${entity?.id}/settings`}>Paramètres</Menu.Item>
      <Menu.Item to="/logout">Se déconnecter</Menu.Item>
    </Menu.Group>
  </Menu>
)

type TopbarProps = {
  entity: EntitySelection
  settings: ApiState<Settings>
}

const Topbar = ({ entity, settings }: TopbarProps) => (
  <header className={styles.topBar}>
    <Logo />

    <nav className={styles.pageNav}>
      {entity?.has_trading && <PageLink to="stocks">Stocks</PageLink>}
      <PageLink to="transactions">Transactions</PageLink>
    </nav>

    <UserMenu settings={settings} entity={entity} />
  </header>
)

export default Topbar
