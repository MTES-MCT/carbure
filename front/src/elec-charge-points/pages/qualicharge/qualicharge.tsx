import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"
import { getQualichargeData } from "./api"
import { Content, Main } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import { useState } from "react"
import { Tabs } from "common/components/tabs2"
import { Navigate, Route, Routes } from "react-router-dom"
import { useQuery } from "common/hooks/async"
import { NoResult } from "common/components/no-result2"
import { Table } from "common/components/table2"
import { QualichargeTab, QualichargeFilter } from "./types"
import { useNotify } from "common/components/notifications"
import { Pagination } from "common/components/pagination2"
import { usePortal } from "common/components/portal"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import {
  useGetFilterOptions,
  useQualichargeColumns,
  useQualichargeQueryBuilder,
} from "./qualicharge.hooks"
import { ValidateDataDialog } from "./components/validate-data-dialog"
import { RecapQuantity } from "common/molecules/recap-quantity"
import { formatNumber } from "common/utils/formatters"
import { Notice } from "common/components/notice"
import { useRoutes } from "common/hooks/routes"
import HashRoute from "common/components/hash-route"
import { QualichargeDataDetail } from "./components/qualicharge-data-detail"
import { useValidateVolumes } from "./hooks/use-validate-volumes"
import useEntity from "common/hooks/entity"
import { ExternalAdminPages } from "common/types"

export const Qualicharge = () => {
  const { state, actions, query, status, years } = useQualichargeQueryBuilder()
  const { t } = useTranslation()
  const notify = useNotify()
  const columns = useQualichargeColumns(status)
  const portal = usePortal()
  const [tab, setTab] = useState(status)
  const routes = useRoutes()
  const entity = useEntity()

  const canValidate = status === QualichargeTab.PENDING

  const { result, loading } = useQuery(getQualichargeData, {
    key: "qualicharge-data",
    params: [query],
  })
  const getFilterOptions = useGetFilterOptions(query)

  const validateVolumes = useValidateVolumes({
    onSuccess: () => {
      actions.setSelection([])
      notify(t("Les volumes ont été validés avec succès."), {
        variant: "success",
      })
    },
  })

  const filterLabels = {
    ...((entity.isAdmin || entity.hasAdminRight(ExternalAdminPages.ELEC)) && {
      [QualichargeFilter.cpo]: t("Aménageur"),
    }),
    ...(status === QualichargeTab.PENDING && {
      [QualichargeFilter.validated_by]: t("Statut"),
    }),
    [QualichargeFilter.operating_unit]: t("Unité d'exploitation"),
    [QualichargeFilter.station_id]: t("Identifiant station"),
    [QualichargeFilter.date_from]: t("Début de la mesure"),
  }

  const openValidateDataModal = () => {
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
        onConfirm={() =>
          Promise.resolve(
            validateVolumes.handleValidateVolumes(state.selection)
          )
        }
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
                  {entity.isCPO && (
                    <Notice
                      linkHref={routes.CONTACT}
                      linkText="ici."
                      icon="ri-error-warning-line"
                      isClosable
                    >
                      En cas de données inexactes, veuillez contacter notre
                      administrateur DGEC
                    </Notice>
                  )}

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
                    rowLink={(row) => ({
                      pathname: location.pathname,
                      search: location.search,
                      hash: `data/${row.id}`,
                    })}
                    topActions={[
                      <Table.TopActionsButton
                        priority="tertiary no outline"
                        iconId="ri-send-plane-line"
                        onClick={openValidateDataModal}
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
        <HashRoute path="data/:id" element={<QualichargeDataDetail />} />
      </Content>
    </Main>
  )
}
