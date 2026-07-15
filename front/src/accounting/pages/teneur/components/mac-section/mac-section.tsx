import { Box, Row } from "common/components/scaffold"
import { Title } from "common/components/title"
import { t } from "i18next"
import { downloadMacFossilFuel } from "../../api"
import { Button } from "common/components/button2"
import { Download } from "common/components/download"
import useEntity from "common/hooks/entity"
import { usePortal } from "common/components/portal"
import { MacDialog } from "../mac-dialog"
import { useAnnualDeclarationTiruert } from "accounting/providers/annual-declaration-tiruert.provider"

export const MacSection = () => {
  const entity = useEntity()
  const portal = usePortal()

  const { selectedYear, currentDeclarationYear = 0 } =
    useAnnualDeclarationTiruert()

  const readOnly = selectedYear < currentDeclarationYear

  const onAddMac = () => {
    portal((close) => (
      <MacDialog
        onClose={close}
        readOnly={readOnly}
        entityId={entity.id}
        year={selectedYear}
      />
    ))
  }

  return (
    <Box>
      <Row>
        <Title is="h1" as="h3">
          {t("Mises à consommation")}
        </Title>
        <Button asideX priority="secondary" onClick={onAddMac}>
          {readOnly ? t("Voir mes MàC") : t("Renseigner mes MàC")}
        </Button>
      </Row>
      <p>
        {t(
          "L'assiette de vos objectifs sera calculée sur la base des mises à consommation de carburants fossiles que vous aurez renseignées, ainsi que d'un PCI théorique."
        )}
      </p>

      <Download
        label={t("Télécharger mes mises à consommation {{year}}", {
          year: selectedYear,
        })}
        linkProps={{
          href: downloadMacFossilFuel(entity.id, selectedYear),
        }}
      />
    </Box>
  )
}
