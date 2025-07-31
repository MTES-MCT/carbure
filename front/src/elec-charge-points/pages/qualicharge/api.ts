import { api } from "common/services/api-fetch"
import { QueryParams } from "common/services/api-fetch.types"
import {
  QualichargeFilter,
  QualichargeTab,
  QualichargeValidatedBy,
  QualichargeQuery,
} from "./types"
import { CBQueryParams } from "common/hooks/query-builder-2"

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

export function getQualichargeFilters(query: QualichargeQuery) {}
export function getQualichargeData(query: QualichargeQuery) {
  const query2 =
    query.status === QualichargeTab.PENDING
      ? { not_validated: true }
      : { validated_by: QualichargeValidatedBy.BOTH }

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
  certificate_ids: number[],
  validated_by: QualichargeValidatedBy
) {
  return api.POST("/elec/provision-certificates-qualicharge/bulk-update/", {
    body: {
      certificate_ids,
      validated_by,
    },
  })
}
