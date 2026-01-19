import { useAnnualDeclarationYears } from "biomethane/hooks/use-annual-declaration-years"
import { Button } from "common/components/button2"
import { ContainerFluid } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import { Text } from "common/components/text"
import { Title } from "common/components/title"
import { useRoutes } from "common/hooks/routes"
import { usePrivateNavigation } from "common/layouts/navigation"
import { formatDate } from "common/utils/formatters"
import { ROUTE_URLS } from "common/utils/routes"
import { Trans, useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"

const currentYear = new Date().getFullYear()
/**
 * This component is used to display a message to the user that the declaration is closed.
 */
export const ClosedDeclaration = () => {
  const { t } = useTranslation()
  const { options: years } = useAnnualDeclarationYears()
  const routes = useRoutes()
  const navigate = useNavigate()

  usePrivateNavigation(t("Période de déclaration fermée"))

  return (
    <ContainerFluid>
      <Title is="h1" as="h5">
        {t("Période de déclaration fermée")}
      </Title>
      <Text size="lg">
        <Trans
          i18nKey="La période de déclaration pour l'année <b>{{year}}</b> est fermée."
          components={{ b: <b /> }}
          values={{ year: currentYear - 1 }}
        />
        <br />
        <Trans
          i18nKey="La prochaine période de déclaration sera ouverte le <b>{{date}}</b>."
          components={{ b: <b /> }}
          values={{ date: formatDate(new Date(currentYear + 1, 0, 1)) }}
        />
      </Text>
      {years.length > 0 ? (
        <Select
          options={years}
          placeholder={t("Consulter mes précédentes déclarations")}
          onChange={(year?: number) => {
            if (year) navigate(routes.BIOMETHANE(year).DIGESTATE)
          }}
        />
      ) : (
        <Button
          linkProps={{ to: ROUTE_URLS.CONTACT }}
          iconId="ri-arrow-right-line"
        >
          {t("Nous contacter pour plus d'informations")}
        </Button>
      )}
    </ContainerFluid>
  )
}
