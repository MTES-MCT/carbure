import React from "react"
import { Trans, useTranslation } from "react-i18next"

import { Link, NavLink } from "common/components/relative-route"
import { Question } from "common/components/icons"

import logoMarianne from "carbure/assets/images/Marianne.svg"
import logoBetaGouv from "carbure/assets/images/carbure.svg"
import styles from "carbure/components/top-bar.module.css"
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

const Topbar = () => {
  const { t } = useTranslation()

  return (
    <header className={styles.topBar}>
      <Logo />
      
      <Box row className={styles.topRight}>
        <LanguageSelection />

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
