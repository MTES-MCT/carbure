import { Header, Row } from "common/components/scaffold"
import { useTranslation } from "react-i18next"
import styles from "./public-navigation.module.css"
import Button from "common/components/button"
import { Logo } from "./logo"
import { LanguageSelection } from "./language-selection"
import { Question } from "common/components/icons"
import { ROUTE_URLS } from "common/utils/routes"

export const PublicNavigation = () => {
  const { t } = useTranslation()
  return (
    <Header>
      <Logo />
      <Row asideX className={styles.menus}>
        <LanguageSelection />
        <Button asideX to="/auth/register" label={t("S'inscrire")} />
        <Button variant="primary" to="/auth/login" label={t("Se connecter")} />
      </Row>
      <a
        href={ROUTE_URLS.USER_GUIDE}
        target="_blank"
        rel="noreferrer"
        className={styles.faq}
      >
        <Question title={t("Guide d'utilisation")} />
      </a>
    </Header>
  )
}
