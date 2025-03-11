import {
  Pagination as DsfrPagination,
  PaginationProps as DsfrPaginationProps,
} from "@codegouvfr/react-dsfr/Pagination"
import { useLocation, useSearchParams } from "react-router-dom"
import cl from "clsx"
import styles from "./pagination.module.css"
import useLocalStorage from "common/hooks/storage"
import { Select } from "../selects2"
import { useTranslation } from "react-i18next"
import { useCallback } from "react"

type PaginationProps = Omit<
  DsfrPaginationProps,
  "getPageLinkProps" | "count"
> & {
  total: number
  limit?: number
  onLimit: (limit: number | undefined) => void
}
/**
 * Same component as the one in the DSFR, but if changes are needed,
 * we can do it here.
 */
export const Pagination = ({
  limit = 10,
  onLimit,
  total,
  ...props
}: PaginationProps) => {
  const pageCount = limit ? Math.ceil(total / limit) : 1
  const [searchParams] = useSearchParams()
  const location = useLocation()
  const { t } = useTranslation()

  const getLabel = useCallback(
    (value: number) => {
      return t("{{count}} par page", { count: value })
    },
    [t]
  )

  return (
    <div className={cl(props.className, styles.pagination)}>
      <Select
        options={[
          { label: getLabel(10), value: 10 },
          { label: getLabel(25), value: 25 },
          { label: getLabel(50), value: 50 },
          { label: getLabel(100), value: 100 },
        ]}
        value={limit}
        onChange={onLimit}
        size="medium"
      />
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
      />
    </div>
  )
}

export function useLimit() {
  return useLocalStorage<number | undefined>("carbure:limit", 10)
}
