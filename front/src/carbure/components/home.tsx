import styles from "./home.module.css"
import banner from "../assets/images/banner.png"
import traders from "../assets/images/traders.svg"
import operators from "../assets/images/operators.svg"
import { Trans } from "react-i18next"
import { ChevronRight } from "common/components/icons"
import { Button } from "common/components/button"
import { Box } from "common/components"

const Home = () => {
  return (
    <main className={styles.home}>
      <section className={styles.homeTitle}>
        <h1>CarbuRe</h1>
        <p>
          <Trans>La plateforme de gestion des biocarburants</Trans>
        </p>
      </section>

      <img className={styles.homeBanner} src={banner} alt="Bannière CarbuRe" />

      <section className={styles.homeContext}>
        <h1>
          <Trans>Qu'est-ce que CarbuRe ?</Trans>
        </h1>

        <p>
          <b>
            <Trans>
              Transmettre des données fiables pour assurer l’essor des
              carburants alternatifs vertueux pour l’environnement
            </Trans>
          </b>
        </p>

        <p>
          <Trans>
            Carbure est un outil développé par le Ministère de la transition
            écologique qui permet aux acteurs de la filière d'échanger
            facilement les informations de durabilité des biocarburants
            circulant en France. L'outil met également a disposition les
            statistiques publiques anonymes des biocarburants incorporés en
            France aux carburants fossiles.
          </Trans>
        </p>

        <a
          href="https://www.ecologie.gouv.fr/biocarburants"
          className={styles.homeExternalLink}
          target="_blank"
          rel="noreferrer"
        >
          <Trans>Plus d’informations sur les biocarburants</Trans>
          <ChevronRight />
        </a>
      </section>

      <Box as="section" row className={styles.homeAuth}>
        <Button as="a" level="primary">
          <Trans>Se connecter</Trans>
        </Button>
        <Button as="a">
          <Trans>S'inscrire</Trans>
        </Button>
      </Box>

      <section className={styles.homeStats}>
        <div className={styles.homeStatsVolume}>
          <h1>1 000 000</h1>
          <p>
            <Trans>
              litres de biocarburants durables déclarés sur CarbuRe cette année
            </Trans>
          </p>
        </div>

        <Box row className={styles.homeStatsEntities}>
          <div className={styles.homeStatsEntityCategory}>
            <h2>10</h2>
            <p>
              <Trans>Opérateurs</Trans>
            </p>
          </div>
          <div className={styles.homeStatsEntityCategory}>
            <h2>10</h2>
            <p>
              <Trans>Producteurs</Trans>
            </p>
          </div>
          <div className={styles.homeStatsEntityCategory}>
            <h2>10</h2>
            <p>
              <Trans>Traders</Trans>
            </p>
          </div>
        </Box>

        <Button level="primary">Voir les statistiques</Button>
      </section>

      <section className={styles.homeExplanation}>
        <h1>
          <Trans>Qui est concerné ?</Trans>
        </h1>

        <Box row className={styles.homeExplanationDetails}>
          <div>
            <h2>
              <Trans>Producteurs et traders de biocarburants</Trans>
            </h2>

            <div>
              <h3>
                <Trans>En tant que producteur ou trader, je peux :</Trans>
              </h3>
              <ul>
                <li>
                  <Trans>
                    Recevoir les informations de durabilité de mes fournisseurs
                  </Trans>
                </li>
                <li>
                  <Trans>
                    Envoyer les informations de durabilité à mes clients
                  </Trans>
                </li>
                <li>
                  <Trans>Gérer mon stock</Trans>
                </li>
              </ul>
            </div>

            <div>
              <h3>
                <Trans>A quoi ça sert ?</Trans>
              </h3>
              <ul>
                <li>
                  <Trans>
                    La plateforme analyse les données et assure la compatibilité
                    avec la réglementation
                  </Trans>
                </li>
                <li>
                  <Trans>
                    Gain de temps et simplification de la gestion de la
                    durabilité
                  </Trans>
                </li>
                <li>
                  <Trans>Transparence vis-à-vis de l'administration</Trans>
                </li>
              </ul>
            </div>
          </div>

          <img
            src={traders}
            className={styles.homeIllustration}
            alt="Traders"
          />
        </Box>

        <Box row className={styles.homeExplanationDetails}>
          <img
            src={operators}
            className={styles.homeIllustration}
            alt="Opérateurs"
          />

          <div>
            <h2>
              <Trans>Opérateurs pétroliers incorporant des biocarburants</Trans>
            </h2>

            <div>
              <h3>
                <Trans>
                  En tant qu'opérateur pétrolier réalisant des incorporations,
                  je peux :
                </Trans>
              </h3>
              <ul>
                <li>
                  <Trans>
                    Recevoir les informations de durabilité de mes fournisseurs
                    des lots incorporés
                  </Trans>
                </li>
                <li>
                  <Trans>Demander simplement des corrections</Trans>
                </li>
              </ul>
            </div>

            <div>
              <h3>
                <Trans>A quoi ça sert ?</Trans>
              </h3>
              <ul>
                <li>
                  <Trans>
                    Garantie de compatibilité avec la réglementation
                  </Trans>
                </li>
                <li>
                  <Trans>
                    Facilité de gestion et gain de temps de déclaration
                  </Trans>
                </li>
                <li>
                  <Trans>Archivage numérique des données de durabilité</Trans>
                </li>
              </ul>
            </div>
          </div>
        </Box>
      </section>
    </main>
  )
}

export default Home
