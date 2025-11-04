import { BiomethaneContract } from "biomethane/pages/contract/types"
import { BiomethaneProductionUnit } from "biomethane/pages/production/types"
import { Button } from "common/components/button2"
import { Text } from "common/components/text"
import { Title } from "common/components/title"
import { useRoutes } from "common/hooks/routes"
import { useTranslation } from "react-i18next"
/**
 * This component is used to display a message to the user that they have not filled in all the settings for their installation.
 */
export const SettingsNotFilled = ({
  contractInfos,
  productionUnit,
}: {
  contractInfos?: BiomethaneContract
  productionUnit?: BiomethaneProductionUnit
}) => {
  const { t } = useTranslation()
  const routes = useRoutes()

  const routeMissingObject =
    contractInfos === undefined
      ? routes.SETTINGS.BIOMETHANE.CONTRACT
      : productionUnit === undefined
        ? routes.SETTINGS.BIOMETHANE.PRODUCTION
        : // Fallback
          routes.SETTINGS.BIOMETHANE.CONTRACT

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
            "Vous n'avez pas encore rempli les informations de votre installation."
          )}
        </Title>
        <Text size="lg">
          {t(
            "Veuillez remplir les informations de votre installation dans les paramètres de votre société."
          )}
        </Text>
        <Button
          linkProps={{ to: routeMissingObject }}
          iconId="ri-arrow-right-line"
        >
          {t("Accéder aux paramètres")}
        </Button>
      </div>
    </div>
  )
}
