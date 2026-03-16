import { BIOMETHANE_HELP_URL } from "biomethane/config"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { Button } from "common/components/button2"
import { NavLink } from "common/components/nav-link"
import { Row } from "common/components/scaffold"
import { Text } from "common/components/text"
import { Title } from "common/components/title"
import { useRoutes } from "common/hooks/routes"
import { useMemo } from "react"
import { Trans, useTranslation } from "react-i18next"

const dataIsNullOrHasErrors = (data: string[] | null | undefined) => {
  return data === null || (data && data.length > 0)
}
/**
 * This component is used to display a message to the user that they have not filled in all the settings for their installation.
 */
export const SettingsNotFilled = () => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const { annualDeclaration } = useAnnualDeclaration()

  const routeMissingObject = useMemo(() => {
    const contractMissingFields =
      annualDeclaration?.missing_fields?.contract_missing_fields
    const productionMissingFields = null
    const injectionMissingFields = null
    // const productionMissingFields =
    //   annualDeclaration?.missing_fields?.production_missing_fields ?? null
    // const injectionMissingFields =
    //   annualDeclaration?.missing_fields?.injection_missing_fields ?? null

    if (dataIsNullOrHasErrors(contractMissingFields)) {
      return routes.SETTINGS.BIOMETHANE.CONTRACT
    }
    if (dataIsNullOrHasErrors(productionMissingFields)) {
      return routes.SETTINGS.BIOMETHANE.PRODUCTION
    }
    if (dataIsNullOrHasErrors(injectionMissingFields)) {
      return routes.SETTINGS.BIOMETHANE.INJECTION
    }

    return routes.SETTINGS.BIOMETHANE.CONTRACT
  }, [
    annualDeclaration?.missing_fields?.contract_missing_fields,
    routes.SETTINGS.BIOMETHANE.CONTRACT,
    routes.SETTINGS.BIOMETHANE.PRODUCTION,
    routes.SETTINGS.BIOMETHANE.INJECTION,
  ])

  const errorsMapping = useMemo(() => {
    const errors = []
    const contractMissingFields =
      annualDeclaration?.missing_fields?.contract_missing_fields

    if (contractMissingFields && contractMissingFields.length > 0) {
      errors.push({
        route: routes.SETTINGS.BIOMETHANE.CONTRACT,
        errors: contractMissingFields,
        name: t("Contrat"),
      })
    }

    return errors
  }, [
    annualDeclaration?.missing_fields?.contract_missing_fields,
    t,
    routes.SETTINGS.BIOMETHANE.CONTRACT,
  ])

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
              defaults="<CustomLink>{{page}}</CustomLink> : il y a <strong>{{count}} champs manquants</strong>."
              values={{ page: error.name, count: error.errors.length }}
              components={{
                CustomLink: <NavLink to={error.route} underline />,
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
