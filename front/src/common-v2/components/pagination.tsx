import { useTranslation } from "react-i18next"
import css from "./pagination.module.css"
import useLocalStorage from "common-v2/hooks/storage"
import { Row } from "./scaffold"
import Button from "./button"
import { ChevronLeft, ChevronRight } from "./icons"
import Select from "./select"
import { Anchors } from "./dropdown"

export interface PaginationProps {
  total: number
  page: number | undefined
  limit: number | undefined
  onPage: (page: number | undefined) => void
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
          anchor={Anchors.topLeft}
          placeholder={t("Choisir une page")}
          value={page}
          onChange={onPage}
          options={listPages(pageCount)}
        />

        <p>{t("sur {{ pageCount }},", { pageCount })}</p>

        <Select
          variant="solid"
          anchor={Anchors.topLeft}
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

// generate a list of numbers from 0 to size-1
export function listPages(size: number) {
  return Array.from(Array(size).keys()).map((i) => ({
    value: i,
    label: `${i + 1}`,
  }))
}

export default Pagination
