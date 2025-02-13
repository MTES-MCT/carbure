import {
  Pagination as DsfrPagination,
  PaginationProps as DsfrPaginationProps,
} from "@codegouvfr/react-dsfr/Pagination"
import { useLocation, useSearchParams } from "react-router-dom"
import cl from "clsx"
import styles from "./pagination.module.css"
import useLocalStorage from "common/hooks/storage"

type PaginationProps = Omit<
  DsfrPaginationProps,
  "getPageLinkProps" | "count"
> & {
  total: number
  limit?: number
}
/**
 * Same component as the one in the DSFR, but if changes are needed,
 * we can do it here.
 */
export const Pagination = ({
  limit = 10,
  total,
  ...props
}: PaginationProps) => {
  const pageCount = limit ? Math.ceil(total / limit) : 1
  const [searchParams] = useSearchParams()
  const location = useLocation()

  return (
    <DsfrPagination
      {...props}
      count={pageCount}
      getPageLinkProps={(page) => {
        const newSearchParams = new URLSearchParams(searchParams)
        newSearchParams.set("page", page.toString())
        return {
          to: `${location.pathname}?${newSearchParams.toString()}`,
        }
      }}
      className={cl(props.className, styles.pagination)}
    />
  )
}

export function useLimit() {
  return useLocalStorage<number | undefined>("carbure:limit", 10)
}
