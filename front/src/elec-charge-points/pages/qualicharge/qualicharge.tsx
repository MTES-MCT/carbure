import useYears from "common/hooks/years-2"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"
import { getQualichargeData, getYears, validateQualichargeVolumes } from "./api"
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
import { useNotify } from "common/components/notifications"
import { Pagination } from "common/components/pagination2"
import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "common/hooks/query-builder-2"
import { usePortal } from "common/components/portal"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import { useGetFilterOptions, useQualichargeColumns } from "./qualicharge.hooks"
import { ValidateDataDialog } from "./components/validate-data-dialog"
import { RecapQuantity } from "common/molecules/recap-quantity"
import { formatNumber } from "common/utils/formatters"
import { Notice } from "common/components/notice"
import { useRoutes } from "common/hooks/routes"

export const useStatus = () => {
  const match = useMatch(
    "/org/:entity/charge-points/qualicharge/:year/:status/*"
  )
  return (match?.params.status ?? QualichargeTab.PENDING) as QualichargeTab
}

export const Qualicharge = () => {
  const { t } = useTranslation()
  const status = useStatus()
  const notify = useNotify()
  const columns = useQualichargeColumns(status)
  const portal = usePortal()
  const years = useYears("/qualicharge", getYears)
  const [tab, setTab] = useState(status)
  const entity = useEntity()
  const routes = useRoutes()

  const { isAdmin, isCPO } = entity
  const validator = isAdmin
    ? QualichargeValidatedBy.DGEC
    : isCPO
      ? QualichargeValidatedBy.CPO
      : undefined

  const canValidate = status === QualichargeTab.PENDING

  const [state, actions] = useCBQueryParamsStore(entity, years.selected, status)

  const query = useCBQueryBuilder(state)

  const { result, loading } = useQuery(getQualichargeData, {
    key: "qualicharge-data-not-validated",
    params: [query],
  })
  const getFilterOptions = useGetFilterOptions(query)

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

  const filterLabels = {
    ...(status === QualichargeTab.PENDING && {
      [QualichargeFilter.validated_by]: t("Statut"),
    }),
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
      <ValidateDataDialog
        volume={volume}
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
                  <Notice
                    linkHref={routes.CONTACT}
                    linkText="ici."
                    icon="ri-error-warning-line"
                    isClosable
                  >
                    En cas de données inexactes, veuillez contacter notre
                    administrateur DGEC
                  </Notice>
                  <RecapQuantity
                    text={t(
                      "{{count}} volumes pour un total de {{total}} MWh",
                      {
                        count: result?.data?.count,
                        total: formatNumber(result?.data?.total_quantity ?? 0, {
                          fractionDigits: 0,
                        }),
                      }
                    )}
                  />
                  <Table
                    rows={result?.data?.results ?? []}
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
                      <Table.TopActionsButton
                        priority="tertiary no outline"
                        iconId="ri-send-plane-line"
                        onClick={openModal}
                        colorVariant="success"
                        disabled={
                          state.selection.length === 0 ||
                          validateVolumes.loading
                        }
                      >
                        {validateVolumes.loading
                          ? t("Validation en cours...")
                          : t("Valider")}
                      </Table.TopActionsButton>,
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
