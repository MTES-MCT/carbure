import React from "react"
import { Trans, useTranslation } from "react-i18next"
import { useLocation } from "react-router-dom"

import { ApiState } from "common/hooks/use-api"
import { EntitySelection } from "carbure/hooks/use-entity"
import { Settings } from "common/types"

import Menu from "common/components/menu"
import { Link, NavLink } from "common/components/relative-route"
import { Question } from "common/components/icons"

import logoMarianne from "../assets/images/Marianne.svg"
import logoBetaGouv from "../assets/images/carbure.svg"
import styles from "./top-bar.module.css"
import Select from "common/components/select"
import { Box } from "common/components"

const Logo = () => (
  <Link to="/" className={styles.logo}>
    <img src={logoMarianne} alt="marianne logo" className={styles.marianne} />
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
  const { t } = useTranslation()
  const location = useLocation()

  const hasRights = settings.data && settings.data.rights.length > 0

  return (
    <Menu className={styles.userMenu} label={entity?.name ?? "Menu"}>
      {hasRights && (
        <Menu.Group label={t("Organisations")}>
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

      <Menu.Group label={settings.data?.email ?? t("Utilisateur")}>
        <Menu.ItemLink relative to="account">
          <Trans>Mon compte</Trans>
        </Menu.ItemLink>
        <Menu.ItemLink to="/logout">
          <Trans>Se déconnecter</Trans>
        </Menu.ItemLink>
      </Menu.Group>
    </Menu>
  )
}

const langOptions = [
  { value: "fr", label: "FR" },
  { value: "en", label: "EN" },
]

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const LanguageSelection = () => {
  const { i18n } = useTranslation()

  return (
    <Select
      level="inline"
      value={i18n.language}
      options={langOptions}
      className={styles.languageSelection}
      style={{ marginLeft: "auto", height: "100%" }}
      onChange={(lang) => i18n.changeLanguage(lang as string)}
    />
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

const Topbar = ({ entity, settings }: TopbarProps) => {
  const { t } = useTranslation()

  return (
    <header className={styles.topBar}>
      <Logo />

      {entity && (
        <nav className={styles.pageNav}>
          {isAdmin(entity) && (
            <PageLink to="dashboard">
              <Trans>Accueil</Trans>
            </PageLink>
          )}

          {canTrade(entity) && (
            <PageLink to="stocks">
              <Trans>Stocks</Trans>
            </PageLink>
          )}

          <PageLink to="transactions">
            <Trans>Transactions</Trans>
          </PageLink>

          {isAdmin(entity) && (
            <React.Fragment>
              <PageLink to="entities">
                <Trans>Sociétés</Trans>
              </PageLink>
            </React.Fragment>
          )}

          {!isAdmin(entity) && (
            <React.Fragment>
              <PageLink to="settings">
                <Trans>Société</Trans>
              </PageLink>
              {/* <PageLink to="stats">
                <Trans>Statistiques</Trans>
              </PageLink> */}
              <PageLink to="registry">
                <Trans>Annuaire</Trans>
              </PageLink>
            </React.Fragment>
          )}
        </nav>
      )}

      <Box row className={styles.topRight}>
        <LanguageSelection />

        <UserMenu settings={settings} entity={entity} />

        <a
          href="https://carbure-1.gitbook.io/faq/"
          target="_blank"
          rel="noreferrer"
          className={styles.faq}
        >
          <Question title={t("Guide d'utilisation")} />
        </a>
      </Box>
    </header>
  )
}

export default Topbar
