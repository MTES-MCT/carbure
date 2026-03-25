import { BIOMETHANE_HELP_URL } from "biomethane/config"
import { Button } from "common/components/button2"
import { NavLink } from "common/components/nav-link"
import { Row } from "common/components/scaffold"
import { Text } from "common/components/text"
import { Title } from "common/components/title"
import { Trans, useTranslation } from "react-i18next"
import { useSettingsNotFilled } from "./use-settings-not-filled"
import { MISSING_FIELDS_HASH } from "../missing-fields/missing-fields.constants"

/**
 * Displays a message when the user has not filled in all the settings for their installation.
 */
export const SettingsNotFilled = () => {
  const { t } = useTranslation()
  const { routeMissingObject, errorsMapping } = useSettingsNotFilled()

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
      }}
    >
      <div
        style={{
          gap: "var(--spacing-2w)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <Title is="h1" as="h5">
          {t(
            "Vous n'avez pas complété toutes les informations de votre installation."
          )}
        </Title>
        <Text size="lg">
          {t(
            "Veuillez remplir les informations (Contrat, Production, Injection) dans les paramètres de votre société."
          )}
        </Text>
        {errorsMapping.map((error) => (
          <Text key={error.route} size="lg">
            <Trans
              defaults="<CustomLink>{{page}}</CustomLink> : <strong>{{count}} informations non renseignées</strong>."
              values={{ page: error.name, count: error.errors.length }}
              components={{
                CustomLink: (
                  <NavLink
                    to={{ pathname: error.route, hash: MISSING_FIELDS_HASH }}
                    underline
                  />
                ),
                strong: <strong />,
              }}
            />
          </Text>
        ))}
        <Row gap="md">
          <Button
            linkProps={{ to: routeMissingObject }}
            iconId="ri-arrow-right-line"
          >
            {t("Accéder aux paramètres")}
          </Button>
          <Button
            priority="secondary"
            linkProps={{ href: BIOMETHANE_HELP_URL, target: "_blank" }}
          >
            {t("Besoin d'aide ?")}
          </Button>
        </Row>
      </div>
    </div>
  )
}
