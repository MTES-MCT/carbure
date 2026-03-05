import { useTranslation } from "react-i18next"
import {
  BiomethaneSupplyInputFilter,
  BiomethaneSupplyInputQuery,
  BiomethaneSupplyInputQueryBuilder,
  BiomethaneSupplyInputSource,
  BiomethaneSupplyInput,
} from "./types"
import { getSupplyPlanInputSource } from "./utils"
import {
  getSupplyPlanInputFilters,
  getSupplyPlanInputs,
  deleteSupplyInput,
} from "./api"
import { defaultNormalizer } from "common/utils/normalize"
import { useSelectedEntity } from "common/providers/selected-entity-provider"
import { useQuery, useMutation } from "common/hooks/async"
import { useQueryBuilder } from "common/hooks/query-builder-2"
import { normalizeDepartment } from "common/utils/normalizers"
import { Button } from "common/components/button2"
import { usePortal } from "common/components/portal"
import useEntity from "common/hooks/entity"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { useNotify, useNotifyError } from "common/components/notifications"

import { Confirm } from "common/components/dialog2"
import { Column } from "common/components/table2"
import { compact } from "common/utils/collection"
import { useSupplyPlanColumns } from "./components/supply-plan-table/supply-plan-table.hooks"

export const useGetFilterOptions = (query: BiomethaneSupplyInputQuery) => {
  const { t } = useTranslation()
  const { selectedEntityId } = useSelectedEntity()

  const filterLabels = {
    [BiomethaneSupplyInputFilter.source]: t("Provenance"),
    [BiomethaneSupplyInputFilter.feedstock]: t("Intrant"),
    [BiomethaneSupplyInputFilter.department]: t("Département"),
  }

  const normalizers = {
    [BiomethaneSupplyInputFilter.feedstock]: (value: string) =>
      defaultNormalizer(value),
    [BiomethaneSupplyInputFilter.source]: (value: string) => ({
      value,
      label: getSupplyPlanInputSource(value as BiomethaneSupplyInputSource),
    }),
    [BiomethaneSupplyInputFilter.department]: (value: string) => {
      const { label, value: normalizedValue } = normalizeDepartment(value)
      return { label, value: normalizedValue }
    },
  }

  return {
    normalizers,
    filterLabels,
    getFilterOptions: (filter: BiomethaneSupplyInputFilter) =>
      getSupplyPlanInputFilters(query, filter, selectedEntityId),
  }
}

export const useSupplyPlanQuery = (year: number) => {
  const { selectedEntityId } = useSelectedEntity()
  const { state, actions, query } = useQueryBuilder<
    BiomethaneSupplyInputQueryBuilder["config"]
  >({
    year,
  })

  const { getFilterOptions, filterLabels, normalizers } =
    useGetFilterOptions(query)

  const { result: supplyInputs, loading } = useQuery(getSupplyPlanInputs, {
    key: `supply-plan-inputs`,
    params: [query, selectedEntityId],
  })

  return {
    queryBuilder: { state, actions, query },
    filterOptions: { getFilterOptions, filterLabels, normalizers },
    supplyPlan: { supplyInputs, loading },
  }
}

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

export const useSupplyPlanProducerColumns = () => {
  const { t } = useTranslation()
  const { openDeleteConfirm, canEditDeclaration } = useDeleteSupplyInput()
  const _columns = useSupplyPlanColumns()

  const columns: Column<BiomethaneSupplyInput>[] = compact([
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

  return [..._columns, ...columns]
}
