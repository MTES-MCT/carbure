import { ElecAdminAuditQuery, ElecAdminAuditStates } from "elec-audit-admin/types"
import { ElecAdminTransferCertificateQuery } from "elec-admin/types"
import { useMemo } from "react"

export function useElectAdminAuditQuery({
  entity,
  year,
  status,
  search,
  page = 0,
  limit,
  order,
  filters,
}: ElecAdminAuditStates) {
  return useMemo<ElecAdminAuditQuery>(
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
