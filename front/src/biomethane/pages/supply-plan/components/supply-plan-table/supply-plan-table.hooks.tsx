import { Cell, Column } from "common/components/table2"
import { useTranslation } from "react-i18next"
import {
  BiomethaneSupplyInput,
  BiomethaneSupplyInputMaterialUnit,
} from "../../types"
import Tag from "@codegouvfr/react-dsfr/Tag"
import {
  convertSupplyPlanInputVolume,
  getSupplyPlanInputSource,
} from "../../utils"
import { getDepartmentName } from "common/utils/geography"
import { formatNumber } from "common/utils/formatters"
import { compact } from "common/utils/collection"
import { useMutation } from "common/hooks/async"
import { deleteSupplyInput } from "../../api"
import { usePortal } from "common/components/portal"
import useEntity from "common/hooks/entity"
import { useSelectedEntity } from "common/providers/selected-entity-provider"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { useNotify, useNotifyError } from "common/components/notifications"
import { Confirm } from "common/components/dialog2"
import { Button } from "common/components/button2"

const useDeleteSupplyInput = () => {
  const { t } = useTranslation()
  const portal = usePortal()
  const entity = useEntity()
  const { selectedEntityId } = useSelectedEntity()
  const { canEditDeclaration, annualDeclarationKey } = useAnnualDeclaration()
  const notify = useNotify()
  const notifyError = useNotifyError()

  const producerEntityId = selectedEntityId ?? entity.id

  const deleteSupplyInputMutation = useMutation(deleteSupplyInput, {
    invalidates: ["supply-plan-inputs", annualDeclarationKey],
    onSuccess: () => {
      notify(t("L'intrant a bien été supprimé."), { variant: "success" })
    },
    onError: (e) => {
      notifyError(e)
    },
  })

  const openDeleteConfirm = (input: BiomethaneSupplyInput) => {
    portal((close) => (
      <Confirm
        title={t("Supprimer l'intrant")}
        description={t("Voulez-vous vraiment supprimer cet intrant ?")}
        confirm={t("Supprimer")}
        icon="ri-close-line"
        customVariant="danger"
        onClose={close}
        onConfirm={() =>
          deleteSupplyInputMutation.execute(producerEntityId, input.id)
        }
        hideCancel
      />
    ))
  }

  return { openDeleteConfirm, canEditDeclaration }
}
export const useSupplyPlanColumns = () => {
  const { t } = useTranslation()
  const { openDeleteConfirm, canEditDeclaration } = useDeleteSupplyInput()

  const columns: Column<BiomethaneSupplyInput>[] = compact([
    {
      header: t("Provenance"),
      cell: (input) =>
        input.source ? (
          <Tag>{getSupplyPlanInputSource(input.source)}</Tag>
        ) : (
          "-"
        ),
    },
    {
      header: t("Intrant"),
      cell: (input) => <Cell text={input.feedstock?.name} />,
    },
    {
      header: t("Département"),
      cell: (input) =>
        input.origin_department && (
          <Tag>{`${input.origin_department} - ${getDepartmentName(input.origin_department) ?? ""}`}</Tag>
        ),
    },
    {
      header: t("Tonnage (tMB)"),
      cell: (input) => {
        if (!input.volume) return <Cell text={t("N/A")} />

        const volume =
          input.material_unit === BiomethaneSupplyInputMaterialUnit.DRY
            ? convertSupplyPlanInputVolume(
                input.volume,
                input.dry_matter_ratio_percent ?? 0
              )
            : input.volume
        return <Cell text={`${formatNumber(volume)} tMB`} />
      },
    },
    canEditDeclaration && {
      header: t("Action"),
      cell: (input) => (
        <Button
          iconId="ri-close-line"
          priority="tertiary no outline"
          title={t("Supprimer")}
          style={{ color: "var(--text-default-grey)" }}
          size="medium"
          captive
          onClick={() => {
            openDeleteConfirm(input)
          }}
        />
      ),
    },
  ])

  return columns
}
