import { Button } from "common/components/button2"
import { Notice } from "common/components/notice"
import { Box, Col, LoaderOverlay, Row } from "common/components/scaffold"
import { Trans, useTranslation } from "react-i18next"
import { ObjectiveSection } from "./components/objective-section"
import { useQuery } from "common/hooks/async"
import { getObjectives } from "./api"
import useEntity from "common/hooks/entity"
import { usePortal } from "common/components/portal"
import { DeclareTeneurDialog } from "./components/declare-teneur-dialog"
import { OverallProgress } from "./components/overall-progress"
import { SectorProgress } from "./components/sector-progress/sector-progress"
import { CappedCategoriesProgress } from "./components/capped-categories-progress"
import { ObjectivizedCategoriesProgress } from "./components/objectivized-categories-progress"
import { UnconstrainedCategoriesProgress } from "./components/unconstrained-categories-progress"
import {
  CategoryObjective,
  TargetType,
  UnconstrainedCategoryObjective,
} from "./types"
import { ValidatePendingTeneurDialog } from "./components/validate-pending-teneur-dialog/validate-pending-teneur-dialog"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useOutletContext } from "react-router-dom"
import { TeneurOutletContext } from "accounting/layouts/teneur-layout"

const Teneur = () => {
  const entity = useEntity()
  const { isAdmin } = entity
  const { t } = useTranslation()
  const portal = usePortal()
  usePrivateNavigation(t("Objectifs annuels"))

  // Récupération du contexte quand disponible (en admin avec entité sélectionnée)
  const outletContext = useOutletContext<TeneurOutletContext>()

  // Appel API normal pour les cas non-admin
  const { result, loading } = useQuery(getObjectives, {
    key: "teneur-objectives",
    params: [entity.id, 2025, isAdmin],
  })

  const isLoadingData = loading || outletContext?.loading
  const objectivesData =
    isAdmin && outletContext?.selectedEntityId
      ? outletContext.objectives
      : result

  if (isLoadingData) {
    return <LoaderOverlay />
  }

  if (isAdmin && !outletContext?.selectedEntityId && !objectivesData) {
    return (
      <Notice noColor variant="info">
        {t("Veuillez sélectionner un redevable pour voir ses objectifs.")}
      </Notice>
    )
  }

  const onCategoryClick = (
    objective: CategoryObjective | UnconstrainedCategoryObjective,
    targetType?: TargetType
  ) => {
    portal((close) => (
      <DeclareTeneurDialog
        onClose={close}
        objective={objective}
        targetType={targetType}
        sectorObjectives={objectivesData?.sectors ?? []}
        mainObjective={objectivesData?.global}
      />
    ))
  }

  const onValidatePendingTeneurClick = () => {
    portal((close) => <ValidatePendingTeneurDialog onClose={close} />)
  }

  return (
    <>
      {isAdmin && outletContext?.selectedEntityId ? (
        <Notice noColor variant="info">
          {t("Vous consultez les objectifs du redevable sélectionné.")}
        </Notice>
      ) : isAdmin ? (
        <Notice noColor variant="info">
          {t("Sur cette page, vous avez accès aux objectifs consolidés.")}
          <br />
          {t(
            "Vous pouvez également sélectionner un redevable pour consulter ses objectifs."
          )}
        </Notice>
      ) : (
        <Notice noColor variant="info">
          {t(
            "Bienvenue dans votre espace de teneur et objectifs annuels. Vous pouvez simuler des conversions quantités et tCO2 eq. évitées, ainsi qu'y rentrer vos quantités de teneur mensuelle afin de clôturer votre comptabilité mensuelle."
          )}
        </Notice>
      )}
      <Box gap="lg">
        {!isAdmin && (
          <Notice noColor variant="info">
            <Row style={{ alignItems: "center", width: "100%" }}>
              <Col spread>
                <p>
                  <Trans
                    t={t}
                    components={{ strong: <strong /> }}
                    defaults="Toutes vos déclarations enregistrées ne sont pas validées, <strong>pensez à valider votre teneur mensuelle</strong> pour que vos déclarations soient prises en comptes."
                  />
                </p>
              </Col>

              <Button priority="primary" onClick={onValidatePendingTeneurClick}>
                {t("Valider ma teneur mensuelle")}
              </Button>
            </Row>
          </Notice>
        )}
        {/* Avancement global */}
        <OverallProgress objective={objectivesData?.global} />
        <SectorProgress sectors={objectivesData?.sectors} />
        <ObjectiveSection
          title={t("Avancement par catégorie de carburants alternatifs")}
        >
          <CappedCategoriesProgress
            categories={objectivesData?.capped_categories}
            onCategoryClick={onCategoryClick}
          />
          <ObjectivizedCategoriesProgress
            categories={objectivesData?.objectivized_categories}
            onCategoryClick={onCategoryClick}
          />
          <UnconstrainedCategoriesProgress
            categories={objectivesData?.unconstrained_categories}
            onCategoryClick={onCategoryClick}
          />
        </ObjectiveSection>
      </Box>
    </>
  )
}

export default Teneur
