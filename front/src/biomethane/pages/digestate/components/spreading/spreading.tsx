import { Button } from "common/components/button2"
import { Table } from "common/components/table2"
import { EditableCard } from "common/molecules/editable-card"
import { useTranslation } from "react-i18next"
import { useSpreadingColumns } from "./spreading.hooks"
import { BiomethaneDigestate } from "../../types"
import { Notice } from "common/components/notice"
import { usePortal } from "common/components/portal"
import { AddSpreadingDepartment } from "./add-spreading-department"
import { useDigestateContext } from "../../digestate.hooks"

export const Spreading = ({
  digestate,
  year,
}: {
  digestate?: BiomethaneDigestate
  year: number
}) => {
  const { t } = useTranslation()
  const columns = useSpreadingColumns()
  const portal = usePortal()
  const { isInDeclarationPeriod } = useDigestateContext()

  const openAddSpreadingDepartmentDialog = () => {
    portal((close) => (
      <AddSpreadingDepartment
        onClose={close}
        year={year}
        spreadings={digestate?.spreadings ?? []}
      />
    ))
  }

  const totalSpreadedArea = digestate?.spreadings.reduce(
    (acc, spreading) => acc + spreading.spread_parcels_area,
    0
  )

  return (
    <EditableCard
      title={t("Épandage")}
      description={
        <>
          {t(
            "Données du plan d'épandage de l'installation à renseigner par département"
          )}
          <br />
          {t("Que si épandage déclaré (dans paramètres)")}
        </>
      }
      headerActions={
        <Button
          iconId="ri-add-line"
          onClick={openAddSpreadingDepartmentDialog}
          disabled={!digestate || !isInDeclarationPeriod}
        >
          {t("Ajouter un département")}
        </Button>
      }
      readOnly={!isInDeclarationPeriod}
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
    </EditableCard>
  )
}
