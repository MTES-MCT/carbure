import { api } from "common/services/api-fetch"
import {
  QualichargeFilter,
  QualichargeTab,
  QualichargeValidatedBy,
  QualichargeQuery,
  QualichargeGroupBy,
} from "./types"
import { apiTypes } from "common/services/api-fetch.types"

const getQuery = (query: QualichargeQuery) => {
  const query2 =
    query.status === QualichargeTab.PENDING
      ? { not_validated: true }
      : { validated_by: [QualichargeValidatedBy.BOTH] }

  return { ...query, ...query2 }
}

export function getYears(entity_id: number) {
  return api
    .GET("/elec/provision-certificates-qualicharge/filters/", {
      params: {
        query: {
          entity_id,
          filter: QualichargeFilter.year,
        },
      },
    })
    .then((response) => ({
      ...response,
      data: response.data?.map((value) => Number(value)) || [],
    }))
}

export function getQualichargeFilters(
  query: QualichargeQuery,
  filter: QualichargeFilter
) {
  return api
    .GET("/elec/provision-certificates-qualicharge/filters/", {
      params: {
        query: {
          ...getQuery(query),
          filter,
        },
      },
    })
    .then((res) => res.data ?? [])
}

const getQualichargeDataResponse = <
  T extends
    | apiTypes["ElecProvisionCertificateQualicharge"]
    | apiTypes["ElecProvisionCertificateQualichargeGrouped"],
>(
  query: QualichargeQuery
) => {
  return api
    .GET("/elec/provision-certificates-qualicharge/", {
      params: {
        query: getQuery(query),
      },
    })
    .then((res) => {
      return {
        ...res,
        data: {
          ...res.data,
          results: res.data?.results as T[],
        },
      }
    })
}
// This endpoint can returned a list of certificates, but when the props group_by is set, it returns a list of grouped certificates
// So we need to force the type of the results to the correct type
export function getQualichargeData(query: QualichargeQuery) {
  return getQualichargeDataResponse<
    apiTypes["ElecProvisionCertificateQualicharge"]
  >(query)
}

export function getQualichargeDataGroupedByOperatingUnit(
  query: QualichargeQuery
) {
  const queryWithGroupBy = {
    ...query,
    group_by: [QualichargeGroupBy.operating_unit],
  }
  return getQualichargeDataResponse<
    apiTypes["ElecProvisionCertificateQualichargeGrouped"]
  >(queryWithGroupBy)
}

export function getQualichargeDataDetail(id: number, entity_id: number) {
  return api.GET(`/elec/provision-certificates-qualicharge/{id}/`, {
    params: {
      query: {
        entity_id,
      },
      path: { id },
    },
  })
}

export function validateQualichargeVolumes(
  entity_id: number,
  certificate_ids: number[],
  validated_by: QualichargeValidatedBy
) {
  return api.POST("/elec/provision-certificates-qualicharge/bulk-update/", {
    params: {
      query: {
        entity_id,
      },
    },
    body: {
      certificate_ids,
      validated_by,
    },
  })
}
