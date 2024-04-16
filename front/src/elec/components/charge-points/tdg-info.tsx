import { Trans, useTranslation } from "react-i18next"
import Alert from "common/components/alert"
import { InfoCircle } from "common/components/icons"
import Tooltip from "common/components/tooltip"
import { ExternalLink } from "common/components/button"

// url vers la page de présentation du projet IRVE de transport.data.gouv.fr
const TDG_URL =
  "https://transport.data.gouv.fr/datasets/fichier-consolide-des-bornes-de-recharge-pour-vehicules-electriques"

// url vers l'explorateur de données IRVE de transport.data.gouv.fr
const TDG_DATA_URL =
  "https://explore.data.gouv.fr/fr/tableau?url=https%3A%2F%2Fwww.data.gouv.fr%2Ffr%2Fdatasets%2Fr%2Feb76d20a-8501-400e-b336-d85724de5435"

export function TDGInfo() {
  const { t } = useTranslation()

  return (
    <Alert icon={InfoCircle} variant="info" style={{ minWidth: "50vw" }}>
      <section>
        <p>
          <Trans
            defaults={`Carbure utilise les <b>données consolidées IRVE</b> de <b>transport.data.gouv.fr</b> pour déterminer certaines caractéristiques de vos points de recharge.`}
          />
        </p>

        <ul
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "var(--spacing-xs)",
            marginTop: "var(--spacing-s)",
          }}
        >
          <li>
            <Trans defaults="Vos PDR y sont identifiés par la colonne <b>id_pdc_itinerance</b>" />
          </li>
          <li>
            <Trans defaults="Le type de courant d'un PDR est considéré comme <b>CC</b> si une des colonnes <b>prise_type_chademo</b> ou <b>prise_type_combo_ccs</b> vaut <b>1</b>. Sinon <b>CA</b>." />
          </li>
          <li>
            <Trans defaults="Si certains PDR d'une station que vous inscrivez sont mentionnés sur <b>transport.data.gouv.fr</b> mais pas dans votre fichier excel, ces PDR seront quand même pris en compte pour déterminer si cette station est soumise ou non à " />
            <Tooltip
              style={{
                display: "inline",
                cursor: "help",
                textDecoration: "underline dotted",
              }}
              title={t(
                "Dérogation prévue par l'article 2 du décret n°2022-1330 permettant pour les stations en courant continu de s'appuyer sur l'indication du PRM du gestionnaire du réseau de distribution pour établir la déclaration prévue à l'article 15-9 du décret n°2019-570"
              )}
            >
              {t("l'article 2 du décret n°2022-1330")}
            </Tooltip>
          </li>
        </ul>

        <p style={{ marginTop: "var(--spacing-m)" }}>
          <ExternalLink href={TDG_DATA_URL}>
            {t("Consulter les données consolidées IRVE")}
          </ExternalLink>
        </p>

        <p
          style={{
            marginTop: "var(--spacing-xs)",
            marginBottom: "var(--spacing-s)",
          }}
        >
          <ExternalLink href={TDG_URL}>
            {t("Voir la documentation IRVE de transport.data.gouv.fr")}
          </ExternalLink>
        </p>
      </section>
    </Alert>
  )
}
