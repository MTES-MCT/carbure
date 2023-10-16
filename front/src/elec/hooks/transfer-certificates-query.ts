import {
  ElecTransferCertificateQuery,
  ElecTransferCertificateStates,
} from "elec/types-cpo"
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
}: ElecTransferCertificateStates) {
  return useMemo<ElecTransferCertificateQuery>(
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
