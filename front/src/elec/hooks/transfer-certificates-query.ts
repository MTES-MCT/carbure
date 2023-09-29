import { ElecCPOTransferCertificateQuery, ElecCPOTransferCertificateStates } from "elec/types-cpo"
import { useMemo } from "react"

export function useTransferCertificatesQuery({
  entity,
  year,
  status,
  search,
  page = 0,
  limit,
  order,
  filters,
}: ElecCPOTransferCertificateStates) {
  return useMemo<ElecCPOTransferCertificateQuery>(
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
