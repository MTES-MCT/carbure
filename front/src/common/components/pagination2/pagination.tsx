import {
  Pagination as DsfrPagination,
  PaginationProps as DsfrPaginationProps,
} from "@codegouvfr/react-dsfr/Pagination"

/**
 * Same component as the one in the DSFR, but if changes are needed,
 * we can do it here.
 */
export const Pagination = (props: DsfrPaginationProps) => {
  return <DsfrPagination {...props} />
}
