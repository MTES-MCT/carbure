import React from "react"
import { Trans, useTranslation } from "react-i18next"
import { useLocation } from "react-router-dom"

import { ApiState } from "common/hooks/use-api"
import useEntity, { EntitySelection } from "carbure/hooks/use-entity"
import { Settings } from "common/types"

import Menu from "common/components/menu"
import { Link, NavLink, Route } from "common/components/relative-route"
import { Question } from "common/components/icons"

import logoRepublique from "../assets/images/republique.svg"
import logoMarianne from "../assets/images/Marianne.svg"
import logoBetaGouv from "../assets/images/betagouvfr.svg"
import styles from "./top-bar.module.css"
import Select from "common/components/select"
import { Box } from "common/components"
import { SettingsGetter } from "settings/hooks/use-get-settings"
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
  return entity && (entity.has_trading || entity.entity_type === "Trader")
}

function isAdmin(entity: EntitySelection) {
  return entity && entity.entity_type === "Administration"
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
            S'inscrire
          </Button>
          <Button
            as="a"
            href="/accounts/login"
            level="primary"
            style={{ marginLeft: 12 }}
          >
            Se connecter
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
  settings: SettingsGetter
}

export const PrivateTopbar = ({ entity, settings }: PrivateTopbarProps) => {
  const { t } = useTranslation()

  return (
    <header className={styles.topBar}>
      <CompactLogo />

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

type TopbarProps = {
  app: AppHook
}

const Topbar = ({ app }: TopbarProps) => {
  const { entity, pending } = useEntity(app)

  if (app.settings.error) {
    return <PublicTopbar />
  } else {
    return <PrivateTopbar entity={entity} settings={app.settings} />
  }
}

export default Topbar
