import { useTranslation } from "react-i18next"
import css from "./pagination.module.css"
import useLocalStorage from "../hooks/storage"
import { Row } from "./scaffold"
import Button from "./button"
import { ChevronLeft, ChevronRight } from "./icons"
import Select from "./select"
import { useSearchParams } from "react-router-dom"

export interface PaginationProps {
  total: number
  page: number
  // With the new backend structure, pagination page starts to 1 instead of 0
  startPage?: number
  limit: number | undefined
  onPage: (page: number) => void
  onLimit: (limit: number | undefined) => void
  keepSearch?: boolean
}

export const Pagination = ({
  total,
  page = 0,
  limit,
  onPage,
  onLimit,
  startPage = 0,
  keepSearch = false,
}: PaginationProps) => {
  const { t } = useTranslation()
  const [searchParams, setSearchParams] = useSearchParams()
  const pageCount = limit ? Math.ceil(total / limit) : 1

  const handlePage = (page: number) => {
    onPage(page)
    if (keepSearch) {
      if (page === startPage) {
        searchParams.delete("page")
      } else {
        searchParams.set("page", `${page}`)
      }

      setSearchParams(searchParams)
    }
  }
  return (
    <Row className={css.pagination}>
      <Button
        disabled={page === startPage}
        variant="secondary"
        icon={ChevronLeft}
        action={() => handlePage(page - 1)}
      />

      <section>
        <p>{t("Page")}</p>

        <Select
          variant="solid"
          anchor="top start"
          placeholder={t("Choisir une page")}
          value={page - startPage}
          onChange={(page) =>
            page !== undefined && handlePage(page + startPage)
          }
          options={listPages(pageCount)}
        />

        <p>{t("sur {{ pageCount }},", { pageCount })}</p>

        <Select
          variant="solid"
          anchor="top start"
          placeholder={t("Tous")}
          value={limit}
          onChange={onLimit}
          options={[
            { value: 10, label: "10" },
            { value: 25, label: "25" },
            { value: 50, label: "50" },
            { value: 100, label: "100" },
          ]}
        />

        <p>{t("résultats")}</p>
      </section>

      <Button
        disabled={page === startPage + pageCount - 1}
        variant="secondary"
        icon={ChevronRight}
        action={() => handlePage(page + 1)}
      />
    </Row>
  )
}

export function useLimit() {
  return useLocalStorage<number | undefined>("carbure:limit", 10)
}

// generate a list of numbers from 0 to size-1
export function listPages(size: number) {
  return Array.from(Array(size).keys()).map((i) => ({
    value: i,
    label: `${i + 1}`,
  }))
}

export default Pagination
