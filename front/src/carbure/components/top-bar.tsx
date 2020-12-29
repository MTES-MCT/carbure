import React from "react"
import { useLocation } from "react-router-dom"

import { ApiState } from "common/hooks/use-api"
import { EntitySelection } from "carbure/hooks/use-entity"
import { Settings } from "common/types"

import Menu from "common/components/menu"
import { Link, NavLink } from "common/components/relative-route"
import { Question } from "common/components/icons"

import logoMarianne from "../assets/images/logo-marianne.svg"
import logoBetaGouv from "../assets/images/betagouvfr.svg"
import styles from "./top-bar.module.css"

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
  const hasRights = settings.data && settings.data.rights.length > 0

  return (
    <Menu className={styles.userMenu} label={entity?.name ?? "Menu"}>
      {hasRights && (
        <Menu.Group label="Organisations">
          {settings.data?.rights.map((right) => (
            <Menu.ItemLink
              key={right.entity.id}
              to={changeOrg(location.pathname, right.entity.id)}
            >
              {right.entity.name}
            </Menu.ItemLink>
          ))}
        </Menu.Group>
      )}

      <Menu.Group label={settings.data?.email ?? "Utilisateur"}>
        <Menu.ItemLink relative to="account">
          Mon compte
        </Menu.ItemLink>
        <Menu.ItemLink to="/logout">Se déconnecter</Menu.ItemLink>
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

      {entity && <PageLink to="transactions">Transactions</PageLink>}

      {isAdmin(entity) && (
        <PageLink to="administration">Administration</PageLink>
      )}

      {entity && <PageLink to="settings">Société</PageLink>}
    </nav>

    <UserMenu settings={settings} entity={entity} />

    <a
      href="https://carbure-1.gitbook.io/faq/"
      target="_blank"
      rel="noreferrer"
      title="FAQ"
      className={styles.faq}
    >
      <Question />
    </a>
  </header>
)

export default Topbar
