import { useEffect } from "react"
import { Link, Route, Routes, useLocation, useNavigate } from "react-router-dom"
import { Trans, useTranslation } from "react-i18next"
import useEntity, { EntityManager } from "carbure/hooks/entity"
import { UserManager, useUserContext } from "carbure/hooks/user"
import Menu from "common-v2/components/menu"
import { Anchors } from "common-v2/components/dropdown"
import { Header } from "common-v2/components/scaffold"
import { ChevronRight, Question } from "common-v2/components/icons"
import Button from "common-v2/components/button"
import Tabs from "common-v2/components/tabs"
import Select from "common-v2/components/select"
import republique from "../assets/images/republique.svg"
import marianne from "../assets/images/Marianne.svg"
import css from "./top-bar.module.css"
import useLocalStorage from "common-v2/hooks/storage"

const Topbar = () => {
  const entity = useEntity()
  const user = useUserContext()

  if (!user.isAuthenticated()) {
    return <PublicTopbar />
  } else {
    return <PrivateTopbar entity={entity} user={user} />
  }
}

const PublicTopbar = () => {
  const { t } = useTranslation()
  return (
    <Header>
      <Logo />
      <LanguageSelection />
      <Button
        aside // prettier-ignore
        href="/accounts/login"
        label={t("S'inscrire")}
      />
      <Button
        variant="primary"
        href="/accounts/login"
        label={t("Se connecter")}
      />
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

      <LanguageSelection />
      <UserMenu user={user} entity={entity} />
    </Header>
  )
}

interface NavigationProps {
  entity: EntityManager
}

const Navigation = ({ entity }: NavigationProps) => {
  const { t } = useTranslation()
  const { isAdmin, isExternal } = entity
  return (
    <Routes>
      <Route
        path="/org/:entity/*"
        element={
          <Tabs
            variant="header"
            tabs={[
              isAdmin && {
                key: "dashboard",
                path: "dashboard",
                label: t("Accueil"),
              },

              !isExternal && {
                key: "transactions",
                path: "transactions-v2",
                label: t("Transactions"),
              },

              isAdmin && {
                key: "entities",
                path: "entities",
                label: t("Sociétés"),
              },

              {
                key: "settings",
                path: "settings",
                label: isAdmin || isExternal ? t("Options") : t("Société"),
              },

              (isAdmin || isExternal) && {
                key: "registry",
                path: "registry",
                label: t("Annuaire"),
              },
            ]}
          />
        }
      />
    </Routes>
  )
}

type Lang = "fr" | "en"
const languages = {
  fr: { key: "fr", label: "Français" },
  en: { key: "en", label: "English" },
}

const LanguageSelection = () => {
  const { i18n } = useTranslation()

  const [lang, setLang] = useLocalStorage(
    "carbure:language",
    i18n.language as Lang
  )

  useEffect(() => {
    i18n.changeLanguage(lang)
  }, [lang, i18n])

  return (
    <Select
      aside
      variant="text"
      value={languages[lang]}
      onChange={(lang) => setLang(lang?.key as Lang)}
      options={Object.values(languages)}
    />
  )
}

interface UserMenuProps {
  user: UserManager
  entity: EntityManager
}

const UserMenu = ({ user, entity }: UserMenuProps) => {
  const { t } = useTranslation()
  const location = useLocation()
  const navigate = useNavigate()

  return (
    <Menu
      variant="text"
      onAction={(item) => navigate(item.path!)}
      label={entity.isBlank ? t("Menu") : entity.name}
      anchor={Anchors.bottomRight}
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
            { label: t("Se déconnecter"), path: "/logout" },
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
