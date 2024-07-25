import {
  ElecAdminProvisionCertificateQuery,
  ElecAdminProvisionCertificateStates,
} from "elec-admin/types"
import { useMemo } from "react"

export function useProvisionCertificatesQuery({
  entity,
  year,
  status,
  search,
  page = 0,
  limit,
  order,
  filters,
}: ElecAdminProvisionCertificateStates) {
  return useMemo<ElecAdminProvisionCertificateQuery>(
    () => ({
      entity_id: entity.id,
      year,
      status,
      search,
      from_idx: page * (limit ?? 0),
      limit: limit || undefined,
      sort_by: order?.column,
      order: order?.direction,
      ...filters,
    }),
    [entity.id, year, status, search, limit, order, filters, page]
  )
}
