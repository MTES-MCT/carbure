import { Trans } from "react-i18next"
import { Link } from "react-router-dom"
import css from "./logo.module.css"
import republique from "common/assets/images/republique.svg"

export const Logo = () => (
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
