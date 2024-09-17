import { CBQueryParams } from "common/hooks/query-builder"

/**
 *
 * @param query Query containing generic parameters used for pagination
 * @param selection A list of ids used for export
 * @returns
 */
export function selectionOrQuery(
  query: Partial<CBQueryParams>,
  selection?: number[]
) {
  if (!selection || selection.length === 0) return query
  else return { entity_id: query.entity_id, selection }
}
