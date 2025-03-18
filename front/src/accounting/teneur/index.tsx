import { Button } from "common/components/button2"
import { Notice } from "common/components/notice"
import { Box, Col, Row } from "common/components/scaffold"
import { Trans, useTranslation } from "react-i18next"
export const Teneur = () => {
  const { t } = useTranslation()
  return (
    <>
      <Notice noColor variant="info">
        {t(
          "Bienvenue dans votre espace de teneur et objectifs annuels. Vous pouvez simuler des conversions quantités et tCO2 eq. évitées, ainsi qu’y rentrer vos quantités de teneur mensuelle afin de clôturer votre comptabilité mensuelle."
        )}
      </Notice>
      <Box>
        <Notice noColor variant="info">
          <Row>
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
      </Box>
    </>
  )
}
