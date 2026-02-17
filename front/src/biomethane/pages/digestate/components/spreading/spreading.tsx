import { Button } from "common/components/button2"
import { Table } from "common/components/table2"
import { ManagedEditableCard } from "common/molecules/editable-card/managed-editable-card"
import { useTranslation } from "react-i18next"
import { useSpreadingColumns } from "./spreading.hooks"
import { BiomethaneDigestate } from "../../types"
import { Notice } from "common/components/notice"
import { usePortal } from "common/components/portal"
import { AddSpreadingDepartment } from "./add-spreading-department"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { useSelectedEntity } from "common/providers/selected-entity-provider"

export const Spreading = ({
  digestate,
}: {
  digestate?: BiomethaneDigestate
}) => {
  const { t } = useTranslation()
  const columns = useSpreadingColumns()
  const portal = usePortal()
  const { canEditDeclaration, selectedYear } = useAnnualDeclaration()
  const { hasSelectedEntity } = useSelectedEntity()

  const openAddSpreadingDepartmentDialog = () => {
    portal((close) => (
      <AddSpreadingDepartment
        onClose={close}
        spreadings={digestate?.spreadings ?? []}
        year={selectedYear}
      />
    ))
  }

  const totalSpreadedArea = digestate?.spreadings.reduce(
    (acc, spreading) => acc + spreading.spread_parcels_area,
    0
  )

  return (
    <ManagedEditableCard
      sectionId="spreading"
      title={t("Épandage")}
      description={
        <>
          {t(
            "Données du plan d'épandage de l'installation à renseigner par département"
          )}
        </>
      }
      headerActions={
        !hasSelectedEntity && (
          <Button
            iconId="ri-add-line"
            onClick={openAddSpreadingDepartmentDialog}
            disabled={!digestate || !canEditDeclaration}
          >
            {t("Ajouter un département")}
          </Button>
        )
      }
      readOnly={!canEditDeclaration}
    >
      {digestate && digestate?.spreadings.length > 0 ? (
        <>
          <Table columns={columns} rows={digestate.spreadings} />
          <Notice>
            {t("Surface totale épandue en digestat (ha) : {{value}}", {
              value: totalSpreadedArea ?? 0,
            })}
          </Notice>
        </>
      ) : (
        <Notice variant="warning" icon="ri-error-warning-line">
          {t("Aucun département d'épandage déclaré")}
        </Notice>
      )}
    </ManagedEditableCard>
  )
}
