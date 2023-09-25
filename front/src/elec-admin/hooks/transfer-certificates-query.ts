import { ElecAdminTransferCertificateQuery, ElecAdminTransferCertificateStates } from "elec-admin/types"
import { ElecCPOTransferCertificateQuery, ElecCPOTransferCertificateStates } from "elec/types"
import { useMemo } from "react"

export function useAdminTransferCertificatesQuery({
  entity,
  year,
  status,
  search,
  page = 0,
  limit,
  order,
  filters,
}: ElecAdminTransferCertificateStates) {
  return useMemo<ElecAdminTransferCertificateQuery>(
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
    [entity.id, status, search, limit, order, filters, page]
  )
}
