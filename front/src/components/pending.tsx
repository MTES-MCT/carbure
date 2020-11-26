import React from "react"
import styles from "./pending.module.css"
import { Link } from "./relative-route"
import { Box, Main, Title } from "./system"
import { AlertTriangle } from "./system/icons"

const Pending = () => (
  <Main className={styles.container}>
    <Title className={styles.welcome}>🌻 Bienvenue sur CarbuRe</Title>
    <p className={styles.subtitle}>
      La plateforme de gestion des flux de biocarburants
    </p>

    <Box className={styles.accountMessage}>
      <span>
        <AlertTriangle className={styles.alertIcon} />
        Il semblerait que votre compte ne soit lié à aucune entité enregistrée
        sur CarbuRe.
      </span>

      <span>
        Veuillez vous rendre vous sur le menu
        <Link relative to="account" className={styles.accountLink}>
          Mon Compte
        </Link>
        pour effectuer une demande d'accès.
      </span>
    </Box>
  </Main>
)

export default Pending
