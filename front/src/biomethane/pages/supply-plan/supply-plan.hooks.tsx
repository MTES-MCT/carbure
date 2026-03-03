import { Cell, Column } from "common/components/table2"
import { useTranslation } from "react-i18next"
import {
  BiomethaneSupplyInput,
  BiomethaneSupplyInputFilter,
  BiomethaneSupplyInputMaterialUnit,
  BiomethaneSupplyInputQuery,
} from "./types"
import Tag from "@codegouvfr/react-dsfr/Tag"
import { convertSupplyPlanInputVolume } from "./utils"
import { getDepartmentName } from "common/utils/geography"
import { deleteSupplyInput, getSupplyPlanInputFilters } from "./api"
import { defaultNormalizer } from "common/utils/normalize"
import { formatNumber } from "common/utils/formatters"
import { useSelectedEntity } from "common/providers/selected-entity-provider"
import { Button } from "common/components/button2"
import { Confirm } from "common/components/dialog2"
import { usePortal } from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { useNotify, useNotifyError } from "common/components/notifications"
import useEntity from "common/hooks/entity"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { compact } from "common/utils/collection"

export const useSupplyPlanColumns = () => {
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

  const columns: Column<BiomethaneSupplyInput>[] = compact([
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

export const useGetFilterOptions = (query: BiomethaneSupplyInputQuery) => {
  const { t } = useTranslation()
  const { selectedEntityId } = useSelectedEntity()

  const filterLabels = {
    [BiomethaneSupplyInputFilter.feedstock]: t("Intrant"),
  }

  const normalizers = {
    [BiomethaneSupplyInputFilter.feedstock]: (value: string) =>
      defaultNormalizer(value),
  }

  return {
    normalizers,
    filterLabels,
    getFilterOptions: (filter: BiomethaneSupplyInputFilter) =>
      getSupplyPlanInputFilters(query, filter, selectedEntityId),
  }
}
