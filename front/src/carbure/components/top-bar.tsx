import { useEffect } from "react"
import { Link, Route, Routes, useLocation, useNavigate } from "react-router-dom"
import { Trans, useTranslation } from "react-i18next"
import useEntity, { EntityManager } from "carbure/hooks/entity"
import { UserManager, useUser } from "carbure/hooks/user"
import useLocalStorage from "common/hooks/storage"
import { useMatomo } from "matomo"
import Menu from "common/components/menu"
import { Header, Row } from "common/components/scaffold"
import Button from "common/components/button"
import Tabs from "common/components/tabs"
import Select from "common/components/select"
import { ChevronRight, Question } from "common/components/icons"
import republique from "../assets/images/republique.svg"
import marianne from "../assets/images/Marianne.svg"
import css from "./top-bar.module.css"
import { compact } from "common/utils/collection"
import Notifications from "./notifications"
import { UserRole } from "carbure/types"

const Topbar = () => {
  const entity = useEntity()
  const user = useUser()

  return (
    <>
      {user.isAuthenticated() ? (
        <PrivateTopbar entity={entity} user={user} />
      ) : (
        <PublicTopbar />
      )}
    </>
  )
}

const PublicTopbar = () => {
  const { t } = useTranslation()
  return (
    <Header>
      <Logo />
      <Row asideX className={css.menus}>
        <LanguageSelection />
        <Button asideX to="/auth/register" label={t("S'inscrire")} />
        <Button variant="primary" to="/auth/login" label={t("Se connecter")} />
      </Row>
      <Faq />
    </Header>
  )
}

interface PrivateTopbarProps {
  user: UserManager
  entity: EntityManager
}

const PrivateTopbar = ({ user, entity }: PrivateTopbarProps) => {
  const { t } = useTranslation()
  const { isBlank } = entity
  const firstEntity = user.getFirstEntity()

  return (
    <Header>
      <LogoCompact />

      {isBlank && firstEntity && (
        <ShortcutLink
          to={`/org/${firstEntity.id}`}
          label={t("Aller sur {{entity}}", { entity: firstEntity.name })}
        />
      )}

      {isBlank && !firstEntity && (
        <ShortcutLink to="pending" label={t("Lier le compte à des sociétés")} />
      )}

      {!isBlank && <Navigation entity={entity} />}

      <Row asideX className={css.menus}>
        <LanguageSelection />
        <UserMenu user={user} entity={entity} />
        <Notifications />
      </Row>

      <Faq />
    </Header>
  )
}

interface NavigationProps {
  entity: EntityManager
}

const Navigation = ({ entity }: NavigationProps) => {
  const { t } = useTranslation()
  const {
    isAdmin,
    isAuditor,
    isIndustry,
    isOperator,
    isPowerOrHeatProducer,
    has_saf,
    isAirline,
    isProducer,
    isCPO,
    has_elec,
  } = entity

  return (
    <Routes>
      <Route
        path="/org/:entity/*"
        element={
          <Tabs
            variant="header"
            tabs={compact([
              isAdmin && {
                key: "dashboard",
                path: "dashboard", // pas encore migré
                label: t("Accueil"),
              },

              (isAdmin || isAuditor) && {
                key: "controls",
                path: "controls", // pas encore migré
                label: t("Biocarburants"),
              },

              isAuditor && {
                key: "elec-audit",
                path: "elec-audit", // pas encore migré
                label: t("Elec"),
              },

              (isIndustry || isPowerOrHeatProducer) && {
                key: "transactions",
                path: "transactions", // ok
                label: t("Transactions"),
              },

              ((has_saf && isOperator) || isAirline) && {
                key: "saf",
                path: "saf", // ok
                label: t("Aviation"),
              },

              ((has_elec && isOperator) || isCPO) && {
                key: "elec",
                path: "elec", // ok
                label: t("Électricité"),
              },

              isCPO && {
                key: "charge-points",
                path: "charge-points", // ok
                label: t("PDC"),
              },

              (isAdmin || entity.hasAdminRight("ELEC")) && {
                key: "elec-admin",
                path: "elec-admin", // pas encore migré
                label: t("Électricité"),
              },

              (isAdmin || entity.hasAdminRight("ELEC")) && {
                key: "elec-admin-audit",
                path: "elec-admin-audit", // pas encore migré
                label: t("PDC"),
              },

              (isOperator || isProducer) && {
                key: "stats",
                path: "stats", // pas encore migré
                label: t("Statistiques"),
              },

              (isAdmin ||
                entity.hasAdminRight("AIRLINE") ||
                entity.hasAdminRight("ELEC") ||
                entity.hasAdminRight("DCA")) && {
                key: "entities",
                path: "entities", // pas encore migré
                label: t("Sociétés"),
              },

              (isAdmin || entity.hasAdminRight("DCA")) && {
                key: "double-counting",
                path: "double-counting", // pas encore migré
                label: t("Double comptage"),
              },

              entity.hasRights(UserRole.Admin, UserRole.ReadWrite) && {
                key: "settings",
                path: "settings", // pas encore migré
                label: t("Société"),
              },

              (isIndustry || isPowerOrHeatProducer) && {
                key: "registry",
                path: "registry", // pas encore migré
                label: t("Annuaire"),
              },
            ])}
          />
        }
      />
    </Routes>
  )
}

type Lang = "fr" | "en"
const languages = [
  { value: "fr", label: "Français" },
  { value: "en", label: "English" },
]

const LanguageSelection = () => {
  const { i18n } = useTranslation()
  const matomo = useMatomo()

  const [lang, setLang] = useLocalStorage<Lang | undefined>(
    "carbure:language",
    i18n.language as Lang
  )

  useEffect(() => {
    i18n.changeLanguage(lang)
  }, [lang, i18n])

  return (
    <Select
      asideX
      variant="text"
      value={lang}
      onChange={(lang) => {
        matomo.push(["trackEvent", "menu", "change-language", lang])
        setLang(lang)
      }}
      options={languages}
    />
  )
}

interface UserMenuProps {
  user: UserManager
  entity: EntityManager
}

const UserMenu = ({ user, entity }: UserMenuProps) => {
  const { t } = useTranslation()
  const matomo = useMatomo()
  const location = useLocation()
  const navigate = useNavigate()

  return (
    <Menu
      variant="text"
      onAction={(path) => {
        if (path.includes("/org")) {
          matomo.push(["trackEvent", "menu", "change-entity", path])
        }
        navigate(path)
      }}
      label={entity.isBlank ? t("Menu") : entity.name}
      anchor="bottom end"
      items={[
        {
          label: t("Organisations"),
          children: user.rights.map((right) => ({
            label: right.entity.name,
            path: changeOrg(location.pathname, right.entity.id),
          })),
        },
        {
          label: user.email,
          children: [
            { label: t("Mon compte"), path: "/account" },
            { label: t("Se déconnecter"), path: "/auth/logout" },
          ],
        },
      ]}
    />
  )
}

function changeOrg(path: string, entity: number) {
  if (!path.includes("org")) return `/org/${entity}`
  else return path.replace(/org\/[0-9]+/, `org/${entity}`)
}

interface ShortcutLinkProps {
  to: string
  label: string
}

const ShortcutLink = ({ to, label }: ShortcutLinkProps) => (
  <Link to={to} className={css.shortcut}>
    {label}
    <ChevronRight />
  </Link>
)

const Faq = () => {
  const { t } = useTranslation()
  return (
    <a
      href="https://carbure-1.gitbook.io/faq/"
      target="_blank"
      rel="noreferrer"
      className={css.faq}
    >
      <Question title={t("Guide d'utilisation")} />
    </a>
  )
}

const Logo = () => (
  <Link to="/" className={css.logo}>
    <img src={republique} alt="marianne logo" className={css.republique} />
    <div className={css.logoText}>
      <h1>CarbuRe</h1>
      <span>
        <Trans>La plateforme de gestion des flux de biocarburants</Trans>
      </span>
    </div>
  </Link>
)

const LogoCompact = () => (
  <Link to="/" className={css.logo}>
    <img src={marianne} alt="marianne logo" className={css.marianne} />
    <h2>CarbuRe</h2>
  </Link>
)

export default Topbar
