import React from "react"
import { Trans, useTranslation } from "react-i18next"
import { useLocation } from "react-router-dom"

import useEntity, { EntitySelection, hasPage } from "carbure/hooks/use-entity"

import { EntityType, ExternalAdminPages } from 'common/types'
import Menu from "common/components/menu"
import { Link, NavLink, Route } from "common/components/relative-route"
import { ChevronRight, Question } from "common/components/icons"

import logoRepublique from "../assets/images/republique.svg"
import logoMarianne from "../assets/images/Marianne.svg"
import styles from "./top-bar.module.css"
import Select from "common/components/select"
import { Box } from "common/components"
import { AppHook } from "carbure/hooks/use-app"
import { Button } from "common/components/button"

const Logo = () => (
  <Link to="/" className={styles.logo}>
    <img
      src={logoRepublique}
      alt="marianne logo"
      className={styles.republique}
    />
    <div className={styles.logoText}>
      <h1>CarbuRe</h1>
      <span>
        <Trans>La plateforme de gestion des flux de biocarburants</Trans>
      </span>
    </div>
  </Link>
)

const CompactLogo = () => (
  <Link to="/" className={styles.logo}>
    <img src={logoMarianne} alt="marianne logo" className={styles.marianne} />
    <h2>CarbuRe</h2>
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
  if (!path.includes("org")) return `/org/${entity}`
  else return path.replace(/org\/[0-9]+/, `org/${entity}`)
}

type UserMenuProps = {
  app: AppHook
  entity: EntitySelection
}

const UserMenu = ({ app, entity }: UserMenuProps) => {
  const { t } = useTranslation()
  const location = useLocation()

  return (
    <Menu className={styles.userMenu} label={entity?.name ?? "Menu"}>
      {app.hasEntities() && (
        <Menu.Group label={t("Organisations")}>
          {app.settings.data?.rights.map((right) => (
            <Menu.ItemLink
              key={right.entity.id}
              to={changeOrg(location.pathname, right.entity.id)}
            >
              {right.entity.name}
            </Menu.ItemLink>
          ))}
        </Menu.Group>
      )}

      <Menu.Group label={app.settings.data?.email ?? t("Utilisateur")}>
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
  { value: "fr", label: "Français" },
  { value: "en", label: "English" },
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
      style={{ marginLeft: "auto" }}
      onChange={(lang) => i18n.changeLanguage(lang as string)}
    />
  )
}

function canTrade(entity: EntitySelection) {
  return entity && (entity.has_trading || entity.entity_type === EntityType.Trader)
}

function isAdmin(entity: EntitySelection) {
  return entity && entity.entity_type === EntityType.Administration
}

function isExternal(entity: EntitySelection) {
  return entity && entity.entity_type === EntityType.ExternalAdmin
}

export const PublicTopbar = () => {
  const { t } = useTranslation()

  return (
    <header className={styles.topBar}>
      <Logo />

      <Box row className={styles.topRight}>
        <Box row style={{ alignItems: "center" }}>
          <LanguageSelection />

          <Button as="a" href="/accounts/register" style={{ marginLeft: 12 }}>
            <Trans>S'inscrire</Trans>
          </Button>
          <Button
            as="a"
            href="/accounts/login"
            level="primary"
            style={{ marginLeft: 12 }}
          >
            <Trans>Se connecter</Trans>
          </Button>
        </Box>

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

type PrivateTopbarProps = {
  entity: EntitySelection
  app: AppHook
}

export const PrivateTopbar = ({ entity, app }: PrivateTopbarProps) => {
  const { t } = useTranslation()

  const firstEntity = app.getFirstEntity()

  return (
    <header className={styles.topBar}>
      <CompactLogo />

      {!entity && firstEntity && (
        <Link to={`/org/${firstEntity.id}`} className={styles.entityShortcut}>
          <Trans>Aller sur {{ entity: firstEntity.name }}</Trans>
          <ChevronRight />
        </Link>
      )}

      {!entity && !firstEntity && (
        <Link to={`/account`} className={styles.entityShortcut}>
          <Trans>Lier le compte à des sociétés</Trans>
          <ChevronRight />
        </Link>
      )}

      {entity && (
        <Route path="/org/:entity">
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

            {!isExternal(entity) && (
              <PageLink to="transactions">
                <Trans>Transactions</Trans>
              </PageLink>
            )}

            {isAdmin(entity) && (
              <React.Fragment>
                <PageLink to="entities">
                  <Trans>Sociétés</Trans>
                </PageLink>
              </React.Fragment>
            )}

            {(isAdmin(entity) || hasPage(entity, ExternalAdminPages.DoubleCounting)) && (
              <PageLink to="double-counting">
                <Trans>Double comptage</Trans>
              </PageLink>
            )}

            {isExternal(entity) && (
              <PageLink to="settings">
                <Trans>Options</Trans>
              </PageLink>
            )}

            {!isAdmin(entity) && !isExternal(entity) && (
              <React.Fragment>
                <PageLink to="settings">
                  <Trans>Société</Trans>
                </PageLink>

                <PageLink to="registry">
                  <Trans>Annuaire</Trans>
                </PageLink>
              </React.Fragment>
            )}
          </nav>
        </Route>
      )}

      <Box row className={styles.topRight}>
        <LanguageSelection />

        <UserMenu app={app} entity={entity} />

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

type TopbarProps = {
  app: AppHook
}

const Topbar = ({ app }: TopbarProps) => {
  const entity = useEntity(app)

  if (!app.isAuthenticated()) {
    return <PublicTopbar />
  } else {
    return <PrivateTopbar entity={entity} app={app} />
  }
}

export default Topbar
