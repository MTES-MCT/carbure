import { Column } from "common/components/table2"
import { useTranslation } from "react-i18next"
import { BiomethaneDigestateSpreading } from "../../types"
import { getDepartmentName } from "common/utils/geography"
import { useMutation } from "common/hooks/async"
import { deleteSpreadingDepartment } from "../../api"
import { useNotify, useNotifyError } from "common/components/notifications"
import { Button } from "common/components/button2"
import { usePortal } from "common/components/portal"
import { Confirm } from "common/components/dialog2"
import useEntity from "common/hooks/entity"
import Tag from "@codegouvfr/react-dsfr/Tag"

export const useSpreadingColumns = () => {
  const { t } = useTranslation()
  const portal = usePortal()
  const deleteSpreading = useDeleteSpreading()
  const entity = useEntity()

  const columns: Column<BiomethaneDigestateSpreading>[] = [
    {
      header: t("Département"),
      cell: (spreadingData) => (
        <Tag
          small
        >{`${spreadingData.spreading_department} - ${getDepartmentName(spreadingData.spreading_department)}`}</Tag>
      ),
    },
    {
      header: t("Quantité épandue (t)"),
      cell: (spreadingData) => spreadingData.spread_quantity,
    },
    {
      header: t("Superficie des parcelles épandues (ha)"),
      cell: (spreadingData) => spreadingData.spread_parcels_area,
    },
    {
      header: t("Actions"),
      cell: (spreadingData) => (
        <Button
          iconId="ri-close-line"
          onClick={() =>
            portal((close) => (
              <Confirm
                title={t("Supprimer le département d'épandage")}
                description={t(
                  "Voulez-vous vraiment supprimer le département d'épandage ?"
                )}
                onConfirm={() =>
                  deleteSpreading.execute(entity.id, spreadingData.id)
                }
                onClose={close}
                confirm={t("Supprimer")}
                hideCancel
                icon="ri-close-line"
              />
            ))
          }
          title="delete department"
          priority="tertiary no outline"
          size="small"
        />
      ),
    },
  ]

  return columns
}

export const useDeleteSpreading = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const notifyError = useNotifyError()

  return useMutation(deleteSpreadingDepartment, {
    invalidates: ["digestate"],
    onSuccess: () => {
      notify(t("Département d'épandage supprimé avec succès"), {
        variant: "success",
      })
    },
    onError: () => notifyError(),
  })
}
