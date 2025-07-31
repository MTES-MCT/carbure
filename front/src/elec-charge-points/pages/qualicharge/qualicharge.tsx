import useYears from "common/hooks/years-2"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"
import {
  getQualichargeData,
  getQualichargeFilters,
  getYears,
  validateQualichargeVolumes,
} from "./api"
import { Content, Main } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import { useState } from "react"
import { Tabs } from "common/components/tabs2"
import { Navigate, Route, Routes, useMatch } from "react-router-dom"
import { useQuery, useMutation } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { NoResult } from "common/components/no-result2"
import { Table } from "common/components/table2"
import {
  QualichargeTab,
  QualichargeValidatedBy,
  QualichargeFilter,
} from "./types"
import { Button } from "common/components/button2"
import { useNotify } from "common/components/notifications"
import { Pagination } from "common/components/pagination2"
import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "common/hooks/query-builder-2"
import { Confirm } from "common/components/dialog2"
import { usePortal } from "common/components/portal"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import { useQualichargeColumns } from "./qualicharge.hooks"

export const useStatus = () => {
  const match = useMatch(
    "/org/:entity/charge-points/qualicharge/:year/:status/*"
  )
  return (match?.params.status ?? QualichargeTab.PENDING) as QualichargeTab
}

export const Qualicharge = () => {
  const { t } = useTranslation()
  const columns = useQualichargeColumns()
  const portal = usePortal()
  const years = useYears("/qualicharge", getYears)
  const [tab, setTab] = useState(QualichargeTab.PENDING)

  const entity = useEntity()
  const { isAdmin, isCPO } = entity
  const validator = isAdmin
    ? QualichargeValidatedBy.DGEC
    : isCPO
      ? QualichargeValidatedBy.CPO
      : undefined
  const status = useStatus()
  const canValidate = status === QualichargeTab.PENDING
  const notify = useNotify()

  const [state, actions] = useCBQueryParamsStore(entity, years.selected, status)

  const query = useCBQueryBuilder(state)

  const { result, loading } = useQuery(getQualichargeData, {
    key: "qualicharge-data-not-validated",
    params: [query],
  })

  const validateVolumes = useMutation(validateQualichargeVolumes, {
    invalidates: ["qualicharge-data-not-validated"],
    onSuccess: () => {
      actions.setSelection([])
      notify(t("Les volumes ont été validés avec succès."), {
        variant: "success",
      })
    },
  })

  const handleValidateVolumes = () => {
    if (state.selection.length > 0) {
      const certificateIds = state.selection
      if (validator) {
        validateVolumes.execute(entity.id, certificateIds, validator)
      }
    }
  }

  const getFilterOptions = (filter: string) =>
    getQualichargeFilters(query, filter as QualichargeFilter)

  const filterLabels = {
    [QualichargeFilter.validated_by]: t("Statut"),
    [QualichargeFilter.operating_unit]: t("Unité d'exploitation"),
    [QualichargeFilter.station_id]: t("Identifiant station"),
    [QualichargeFilter.date_from]: t("Début de la mesure"),
  }

  const openModal = () => {
    const qualichargeRows =
      result?.data?.results?.filter((qualichargeData) =>
        state.selection.includes(qualichargeData.id)
      ) ?? []
    const volume = qualichargeRows?.reduce(
      (sum, data) => sum + data.energy_amount,
      0
    )
    portal((close) => (
      <Confirm
        title={t("Confirmer votre action")}
        description={
          <>
            <p>
              {t(
                "Êtes-vous sûr de valider l’ensemble des données Qualicharge sélectionnées ?"
              )}
            </p>
            <p>
              {t(
                "Votre compte sera crédité de certificats ENR à hauteur de {{volume}} MWH, une fois la validation DGEC effectuée.",
                {
                  volume,
                }
              )}
            </p>
          </>
        }
        confirm={t("Valider")}
        icon="ri-check-line"
        variant="primary"
        onConfirm={() => Promise.resolve(handleValidateVolumes())}
        onClose={close}
      />
    ))
  }

  usePrivateNavigation(t("Données Qualicharge"))
  return (
    <Main>
      <Select
        loading={years.loading}
        placeholder={t("Choisir une année")}
        value={years.selected}
        onChange={years.setYear}
        options={years.options}
        sort={(year) => -year.value}
      />

      <Tabs
        keepSearch
        focus={tab}
        onFocus={setTab}
        tabs={[
          {
            key: QualichargeTab.PENDING,
            path: QualichargeTab.PENDING,
            label: t("En attente"),
            icon: "ri-draft-line",
            iconActive: "ri-draft-fill",
          },
          {
            key: QualichargeTab.VALIDATED,
            path: QualichargeTab.VALIDATED,
            label: t("Validés"),
            icon: "ri-send-plane-line",
            iconActive: "ri-send-plane-fill",
          },
        ]}
      />
      <Content>
        <FilterMultiSelect2
          filterLabels={filterLabels}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={getFilterOptions}
        />
        <Routes>
          <Route
            path="/:status"
            element={
              !loading && result?.data?.results?.length === 0 ? (
                <NoResult />
              ) : (
                <>
                  <Table
                    rows={result?.data?.results ?? []}
                    //onAction={}
                    columns={columns}
                    loading={loading}
                    hasSelectionColumn={canValidate}
                    selected={state.selection}
                    onSelect={actions.setSelection}
                    identify={(row) => row.id}
                    selectionText={t("{{count}} volumes sélectionnés", {
                      count: state.selection.length,
                    })}
                    topActions={[
                      <Button
                        priority="tertiary no outline"
                        iconId="ri-send-plane-line"
                        onClick={openModal}
                        disabled={
                          state.selection.length === 0 ||
                          validateVolumes.loading
                        }
                        key="validate-volumes"
                      >
                        {validateVolumes.loading
                          ? t("Validation en cours...")
                          : t("Valider")}
                      </Button>,
                    ]}
                  />
                  <Pagination
                    defaultPage={query.page}
                    total={result?.data?.count ?? 0}
                    limit={state.limit}
                    onLimit={actions.setLimit}
                    disabled={loading}
                  />
                </>
              )
            }
          />
          <Route path="*" element={<Navigate to={QualichargeTab.PENDING} />} />
        </Routes>
      </Content>
    </Main>
  )
}
