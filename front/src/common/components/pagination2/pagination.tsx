import {
  Pagination as DsfrPagination,
  PaginationProps as DsfrPaginationProps,
} from "@codegouvfr/react-dsfr/Pagination"
import { useLocation, useSearchParams } from "react-router-dom"

/**
 * Same component as the one in the DSFR, but if changes are needed,
 * we can do it here.
 */
export const Pagination = (props: DsfrPaginationProps) => {
  const [searchParams] = useSearchParams()
  const location = useLocation()

  return (
    <DsfrPagination
      {...props}
      getPageLinkProps={(page) => {
        const newSearchParams = new URLSearchParams(searchParams)
        newSearchParams.set("page", page.toString())
        return {
          to: `${location.pathname}?${newSearchParams.toString()}`,
        }
      }}
    />
  )
}
