import { useAnnualDeclarationYear } from "biomethane/providers/annual-declaration"
import { Button } from "common/components/button2"
import { ContainerFluid } from "common/components/scaffold"
import { Text } from "common/components/text"
import { Title } from "common/components/title"
import { usePrivateNavigation } from "common/layouts/navigation"
import { ROUTE_URLS } from "common/utils/routes"
import { useTranslation } from "react-i18next"

export const DeclarationNotFound = () => {
  const { t } = useTranslation()
  usePrivateNavigation(t("Déclaration non trouvée"))
  const yearParam = useAnnualDeclarationYear()

  return (
    <ContainerFluid>
      <Title is="h1" as="h5">
        {t("Déclaration non trouvée pour l'année {{year}}", {
          year: yearParam,
        })}
      </Title>
      <Text size="lg">
        {t("Veuillez nous contacter si le problème persiste.")}
      </Text>
      <Button
        linkProps={{ to: ROUTE_URLS.CONTACT }}
        iconId="ri-arrow-right-line"
      >
        {t("Contacter l'administration")}
      </Button>
    </ContainerFluid>
  )
}
