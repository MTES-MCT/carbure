import { Trans, useTranslation } from "react-i18next"
import Alert from "common/components/alert"
import { InfoCircle } from "common/components/icons"
import Tooltip from "common/components/tooltip"
import { ExternalLink } from "common/components/button"

export function TDGInfo() {
  const { t } = useTranslation()

  return (
    <Alert icon={InfoCircle} variant="info" style={{ minWidth: "50vw" }}>
      <section>
        <p>
          {t("Carbure utilise les")}{" "}
          <ExternalLink href="https://www.data.gouv.fr/fr/datasets/5448d3e0c751df01f85d0572/">
            <b>{t("données consolidées IRVE")}</b>
          </ExternalLink>{" "}
          <Trans defaults="de <b>transport.data.gouv.fr</b> pour déterminer certaines caractéristiques de vos points de recharge." />
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
            {t("Vos PDR y sont identifiés par la colonne")}{" "}
            <ExternalLink href="https://schema.data.gouv.fr/etalab/schema-irve-statique/2.3.1/documentation.html#propriete-id-pdc-itinerance">
              <b>id_pdc_itinerance</b>
            </ExternalLink>
          </li>
          <li>
            <Trans defaults="Le type de courant d'un PDR est considéré comme <b>CC</b> si une des colonnes " />
            <ExternalLink href="https://schema.data.gouv.fr/etalab/schema-irve-statique/2.3.1/documentation.html#propriete-prise-type-chademo">
              <b>prise_type_chademo</b>
            </ExternalLink>{" "}
            {t("ou")}{" "}
            <ExternalLink href="https://schema.data.gouv.fr/etalab/schema-irve-statique/2.3.1/documentation.html#propriete-prise-type-combo-ccs">
              <b>prise_type_combo_ccs</b>
            </ExternalLink>{" "}
            <Trans defaults="vaut <b>1</b>. Sinon <b>CA</b>." />
          </li>
          <li>
            <Trans defaults="Si certains PDR d'une station que vous inscrivez sont mentionnés sur <b>transport.data.gouv.fr</b> mais pas dans votre fichier excel, ces PDR seront quand même pris en compte pour déterminer si cette station est soumise ou non à" />{" "}
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
          <li>
            {t(
              "Si certaines erreurs vous suprennent (ex: MID obligatoire sur un point CC), vous pouvez remplir les 2 colonnes optionnelles à droite du fichier excel pour nous indiquer la bonne valeur à utiliser dans nos calculs."
            )}
          </li>
        </ul>

        <p
          style={{
            marginTop: "var(--spacing-m)",
            marginBottom: "var(--spacing-s)",
          }}
        >
          <ExternalLink href="https://explore.data.gouv.fr/fr/tableau?url=https%3A%2F%2Fwww.data.gouv.fr%2Ffr%2Fdatasets%2Fr%2Feb76d20a-8501-400e-b336-d85724de5435">
            {t("Explorer les données consolidées IRVE")}
          </ExternalLink>
        </p>
      </section>
    </Alert>
  )
}
