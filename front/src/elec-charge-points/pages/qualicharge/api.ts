import { api } from "common/services/api-fetch"
import {
  QualichargeFilter,
  QualichargeTab,
  QualichargeValidatedBy,
  QualichargeQuery,
} from "./types"
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
          ...query,
          filter,
        },
      },
    })
    .then((res) => res.data ?? [])
}
export function getQualichargeData(query: QualichargeQuery) {
  const query2 =
    query.status === QualichargeTab.PENDING
      ? { not_validated: true }
      : { validated_by: [QualichargeValidatedBy.BOTH] }

  return api.GET("/elec/provision-certificates-qualicharge/", {
    params: {
      query: {
        ...query,
        ...query2,
      },
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
