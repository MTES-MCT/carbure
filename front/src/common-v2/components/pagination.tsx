import { useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import useLocalStorage from "common-v2/hooks/storage"
import { Row } from "./scaffold"
import css from "./pagination.module.css"
import Button from "./button"
import { ChevronLeft, ChevronRight } from "./icons"
import Select from "./select"
import { Anchors } from "./dropdown"

export interface PaginationProps {
  total: number
  page: number
  limit: number
  onPage: (page: number) => void
  onLimit: (limit: number) => void
}

export const Pagination = ({
  total,
  page,
  limit,
  onPage,
  onLimit,
}: PaginationProps) => {
  const { t } = useTranslation()

  const pageCount = limit ? Math.ceil(total / limit) : 1
  const pages = listPages(pageCount)

  const limits = [
    { key: 10, label: "10" },
    { key: 25, label: "25" },
    { key: 50, label: "50" },
    { key: 100, label: "100" },
    { key: 0, label: t("Tous") },
  ]

  return (
    <Row className={css.pagination}>
      <Button
        disabled={page === 0}
        variant="secondary"
        icon={ChevronLeft}
        action={() => onPage(page - 1)}
      />

      <section>
        <p>{t("Page")}</p>

        <Select
          variant="solid"
          anchor={Anchors.topLeft}
          placeholder={t("Choisir une page")}
          value={pages.find((p) => p.key === page)}
          onChange={(page) => onPage(page!.key)}
          options={pages}
        />

        <p>{t("sur {{ pageCount }},", { pageCount })}</p>

        <Select
          variant="solid"
          anchor={Anchors.topLeft}
          value={limits.find((l) => l.key === limit)!}
          onChange={(limit) => onLimit(limit!.key)}
          options={limits}
        />

        <p>{t("résultats")}</p>
      </section>

      <Button
        disabled={page === pageCount - 1}
        variant="secondary"
        icon={ChevronRight}
        action={() => onPage(page + 1)}
      />
    </Row>
  )
}

export interface PaginationManager {
  page: number
  limit: number
  setPage: (page: number) => void
  setLimit: (limit: number) => void
}

export function usePagination() {
  const [page, setPage] = useState(0)
  const [limit, setLimit] = useLocalStorage<number>("carbure:limit", 10) // prettier-ignore

  useEffect(() => {
    setPage(0)
  }, [limit])

  return { page, limit, setPage, setLimit }
}

// generate a list of numbers from 0 to size-1
export function listPages(size: number) {
  return Array.from(Array(size).keys()).map((i) => ({
    key: i,
    label: `${i + 1}`,
  }))
}

export default Pagination
