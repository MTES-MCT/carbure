import { Button } from "common/components/button2"
import { Notice } from "common/components/notice"
import { Box, Col, LoaderOverlay, Row } from "common/components/scaffold"
import { Trans, useTranslation } from "react-i18next"
import { ObjectiveSection } from "./components/objective-section"
import { CardProgress } from "./components/card-progress"
import { useQuery } from "common/hooks/async"
import { getObjectives } from "./api"
import useEntity from "common/hooks/entity"
import { Text } from "common/components/text"
export const Teneur = () => {
  const entity = useEntity()
  const { t } = useTranslation()

  const { result, loading } = useQuery(getObjectives, {
    key: "teneur-objectives",
    params: [entity.id, 2025],
  })

  if (loading) {
    return <LoaderOverlay />
  }

  return (
    <>
      <Notice noColor variant="info">
        {t(
          "Bienvenue dans votre espace de teneur et objectifs annuels. Vous pouvez simuler des conversions quantités et tCO2 eq. évitées, ainsi qu’y rentrer vos quantités de teneur mensuelle afin de clôturer votre comptabilité mensuelle."
        )}
      </Notice>
      <Box>
        <Notice noColor variant="info">
          <Row style={{ alignItems: "center" }}>
            <Col spread>
              <p>
                <Trans
                  t={t}
                  components={{ strong: <strong /> }}
                  defaults="Toutes vos déclarations enregistrées ne sont pas validées, <strong>pensez à valider votre teneur mensuelle</strong> pour que vos déclarations soient prises en comptes."
                />
              </p>
            </Col>

            <Button priority="primary">
              {t("Valider ma teneur mensuelle")}
            </Button>
          </Row>
        </Notice>
        {/* Avancement global */}

        <ObjectiveSection
          title={t("Avancement global")}
          description={t(
            "Ces objectifs sont calculés sur la base de vos mises à la consommation décadaires. Ces mises à la consommation ne sont pas consolidées et sont calculées sur la base d’un PCI théorique."
          )}
        >
          {result && (
            <CardProgress
              title={t("Total annuel à la date du {{date}}", {
                date: "15/03/2025",
              })}
              description={t(
                "Objectif en tC02 évitées en {{date}}: {{objective}} tC02 évitées",
                {
                  date: "2025",
                  objective: result.global.objective,
                }
              )}
              mainValue={result.global.teneur_declared}
              mainText={t("tCO2 évitées")}
              baseQuantity={result.global.teneur_declared}
              targetQuantity={result.global.objective}
              declaredQuantity={result.global.teneur_declared_month}
              badge={
                <CardProgress.DefaultBadge
                  targetQuantity={result.global.objective}
                  declaredQuantity={
                    result.global.teneur_declared +
                    result.global.teneur_declared_month
                  }
                />
              }
            >
              <ul>
                <Text is="li" size="sm">
                  {t("Teneur déclarée ce mois :")}{" "}
                  {t("{{count}} tCO2 évitées", {
                    count: result.global.teneur_declared_month,
                  })}
                </Text>
                <Text is="li" size="sm">
                  {t("Volume disponible :")}{" "}
                  {t("{{count}} tCO2 évitées", {
                    count: result.global.quantity_available,
                  })}
                </Text>
              </ul>
            </CardProgress>
          )}
        </ObjectiveSection>
        <ObjectiveSection
          title={t("Avancement par filière")}
          description={t("Retrouvez ici votre suivi d’objectif par filière.")}
        ></ObjectiveSection>
      </Box>
    </>
  )
}
