import { useTranslation } from "react-i18next"
import css from "./pagination.module.css"
import useLocalStorage from "../hooks/storage"
import { Row } from "./scaffold"
import Button from "./button"
import { ChevronLeft, ChevronRight } from "./icons"
import Select from "./select"

export interface PaginationProps {
  total: number
  page: number
  limit: number | undefined
  onPage: (page: number) => void
  onLimit: (limit: number | undefined) => void
}

export const Pagination = ({
  total,
  page = 0,
  limit,
  onPage,
  onLimit,
}: PaginationProps) => {
  const { t } = useTranslation()
  const pageCount = limit ? Math.ceil(total / limit) : 1

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
          anchor="top start"
          placeholder={t("Choisir une page")}
          value={page}
          onChange={(page) => page !== undefined && onPage(page)}
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
            { value: undefined, label: t("Tous") },
          ]}
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
