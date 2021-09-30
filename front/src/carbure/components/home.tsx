import cl from "clsx"
import styles from "./home.module.css"
import banner from "../assets/images/banner.png"
import traders from "../assets/images/traders.svg"
import operators from "../assets/images/operators.svg"
import schema from "../assets/images/schema.svg"
import { Trans } from "react-i18next"
import {
  ChevronRight,
  ExternalLink,
  Loader,
  Plus,
  UserAdd,
  UserCheck,
} from "common/components/icons"
import { Button } from "common/components/button"
import { EntityType } from "common/types"
import api from "common/services/api"
import useAPI from "common/hooks/use-api"
import { Fragment, useEffect } from "react"
import { AppHook } from "carbure/hooks/use-app"

interface HomeStats {
  total_volume: number
  entities: {
    [EntityType.Operator]: number
    [EntityType.Trader]: number
    [EntityType.Producer]: number
  }
}

function fetchHomeStats() {
  return api.get<HomeStats>("/common/stats")
}

type HomeProps = {
  app: AppHook
}

const Home = ({ app }: HomeProps) => {
  const [stats, getStats] = useAPI(fetchHomeStats)

  useEffect(() => {
    getStats()
  }, [getStats])

  const firstEntity = app.getFirstEntity()

  return (
    <main className={styles.home}>
      <section className={styles.homeTitle}>
        <h1>CarbuRe</h1>
        <p>
          <Trans>La plateforme de gestion des flux de biocarburants</Trans>
        </p>
      </section>

      <img className={styles.homeBanner} src={banner} alt="Bannière CarbuRe" />

      <section className={styles.homeContext}>
        <div>
          <h1>
            <Trans>Qu'est-ce que CarbuRe ?</Trans>
          </h1>

          <h2>
            <Trans>
              Transmettre des données fiables pour assurer l’essor des
              carburants alternatifs vertueux pour l’environnement.
            </Trans>
          </h2>

          <p>
            <Trans>
              Carbure est un outil développé par le Ministère de la Transition
              Ecologique qui permet aux acteurs de la filière d'échanger
              facilement les informations de durabilité des biocarburants
              circulant en France. L'outil met également à disposition des
              statistiques publiques anonymes des biocarburants incorporés en
              France aux carburants fossiles.
            </Trans>
          </p>

          <a
            href="https://www.ecologie.gouv.fr/biocarburants"
            target="_blank"
            rel="noreferrer"
          >
            <Trans>Plus d’informations sur les biocarburants</Trans>
            <ChevronRight />
          </a>
        </div>

        <img src={schema} alt="Schéma" className={styles.homeSchema} />
      </section>

      <section className={styles.homeAuthentication}>
        {!app.isAuthenticated() ? (
          <Fragment>
            <Button
              icon={UserAdd}
              as="a"
              href="/accounts/register"
              className={styles.homeButton}
            >
              <Trans>S'inscrire</Trans>
            </Button>
            <Button
              icon={UserCheck}
              as="a"
              level="primary"
              href="/accounts/login"
              className={styles.homeButton}
            >
              <Trans>Se connecter</Trans>
            </Button>
          </Fragment>
        ) : firstEntity ? (
          <Button
            icon={ExternalLink}
            as="a"
            level="primary"
            href={`/v2/org/${firstEntity.id}`}
            className={styles.homeButton}
          >
            <Trans>Aller sur {{ entity: firstEntity.name }}</Trans>
          </Button>
        ) : (
          <Button
            icon={Plus}
            as="a"
            level="primary"
            href="/v2/account"
            className={styles.homeButton}
          >
            <Trans>Lier le compte à des sociétés</Trans>
          </Button>
        )}
      </section>

      <section className={styles.homeStats}>
        <div className={cl(styles.homeStatsBlock, styles.homeStatsVolume)}>
          <h1>
            {stats.loading ? (
              <Loader />
            ) : (
              Math.round(stats.data?.total_volume ?? 0).toLocaleString("fr")
            )}
            {" m³"}
          </h1>
          <p>
            <Trans>de biocarburants durables</Trans>
          </p>
          <p>
            <Trans>déclarés sur CarbuRe cette année</Trans>
          </p>
        </div>

        <div className={styles.homeStatsEntities}>
          <div className={styles.homeStatsBlock}>
            <h1>
              {stats.loading ? (
                <Loader />
              ) : (
                stats.data?.entities[EntityType.Operator]
              )}
            </h1>
            <p>
              <Trans>Opérateurs</Trans>
            </p>
          </div>
          <div className={styles.homeStatsBlock}>
            <h1>
              {stats.loading ? (
                <Loader />
              ) : (
                stats.data?.entities[EntityType.Producer]
              )}
            </h1>
            <p>
              <Trans>Producteurs</Trans>
            </p>
          </div>
          <div className={styles.homeStatsBlock}>
            <h1>
              {stats.loading ? (
                <Loader />
              ) : (
                stats.data?.entities[EntityType.Trader]
              )}
            </h1>
            <p>
              <Trans>Traders</Trans>
            </p>
          </div>
        </div>

        <Button
          icon={ExternalLink}
          as="a"
          href="/v2/public_stats"
          className={styles.homeButton}
          rel="noreferrer"
          target="_blank"
        >
          <Trans>Voir les statistiques</Trans>
        </Button>
      </section>

      <section className={styles.homeEntities}>
        <h1 className={styles.homeSectionTitle}>
          <Trans>Qui est concerné ?</Trans>
        </h1>

        <section className={styles.homeProducers}>
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
        </section>

        <section className={styles.homeOperators}>
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
        </section>
      </section>
    </main>
  )
}

export default Home
