import { useState } from "react"
import { Button } from "common/components/button2"
import { useHashMatch } from "common/components/hash-route"
import { useQuery } from "common/hooks/async"
import { useNavigation } from "./navigation.hooks"
import { getNeighborsInfos } from "./navigation.utils"
import { useTranslation } from "react-i18next"
import cl from "clsx"
import css from "./navigation.module.css"
import { useSearchParams } from "react-router-dom"

const getItemsIds = (items: { id: number }[]) => items.map((item) => item.id)

const getKeyByValue = (map: Map<number, number[]>, value: number) => {
  return [...map.entries()].find(([, val]) => val.includes(value))?.[0]
}

export type NavigationButtonsProps = {
  // Call the backend to retrieve ids based on page
  fetchIdsForPage: (page: number) => Promise<{ id: number }[]>

  // ids already retrieved to avoid unecessary http calls
  baseIdsList?: number[]
  // Total of elements
  total: number
  // Limit per page
  limit?: number
}

/**
 * This component is designed to work with a table that displays a list of data, and a modal that shows details
 * when a row in the table is clicked.
 *
 * When the modal is opened, this component provides "Previous" and "Next" buttons to navigate through the data.
 * It retrieves the IDs of the previous and next entries using the `fetchIdsForPage` function prop, which loads
 * the IDs for a specific page of data from the backend.
 *
 * The component handles fetching new pages when necessary, allowing smooth navigation across the list.
 */
const NavigationButtons = ({
  fetchIdsForPage,
  baseIdsList = [],
  total,
  limit,
}: NavigationButtonsProps) => {
  const { t } = useTranslation()
  const match = useHashMatch(":root/:id")
  const [searchParams] = useSearchParams()
  const searchParamsPage = searchParams.get("page")

  const basePage = searchParamsPage ? parseInt(searchParamsPage) : 1

  // Get the current id from url
  const current = parseInt(match?.params.id ?? "")

  // build a map containing a list of ids per page
  const [idsMap, setIdsMap] = useState(
    new Map<number, number[]>(
      baseIdsList.length ? [[basePage, baseIdsList]] : []
    )
  )

  // find the page associated to the current id
  const page = getKeyByValue(idsMap, current) ?? 1

  // list of ids for the current page
  const currentPageIds = idsMap.get(page) || []

  // Number of pages
  const pageCount = limit ? Math.ceil(total / limit) : 1

  const nav = useNavigation(idsMap, page, pageCount)

  const fetchIdsForNavigation = async (page: number) => {
    if (idsMap.has(page)) {
      const ids = idsMap.get(page) || []
      return Promise.resolve(ids.map((id) => ({ id })))
    }
    const items = await fetchIdsForPage(page)

    if (items && !idsMap.has(page)) {
      setIdsMap(new Map(idsMap.set(page, getItemsIds(items))))
    }

    return items
  }
  const { loading } = useQuery(
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    (current: number) => fetchIdsForNavigation(page),
    {
      key: "ids-navigation",
      params: [current],
      onSuccess: (res) => {
        const infos = getNeighborsInfos(
          new Map([[page, getItemsIds(res)]]),
          current,
          page,
          pageCount
        )

        // Fetch previous page only if the current id is first id of the current page and there is a previous page
        if (infos.hasPrev && !infos.hasPrevCurrentPage) {
          fetchIdsForNavigation(page - 1)
        } else if (infos.hasNext && !infos.hasNextCurrentPage) {
          // Fetch next page only if the current id is last id of the current page and there is a next page
          fetchIdsForNavigation(page + 1)
        }
      },
    }
  )

  if (!currentPageIds) return null

  return (
    <div data-asidex={true} className={cl(css.navigation)}>
      <Button
        priority="secondary"
        disabled={!nav.hasPrev && page === 1}
        loading={loading}
        iconId="ri-arrow-left-s-line"
        onClick={nav.prev}
      >
        {t("Précédent")}
      </Button>
      <Button
        priority="secondary"
        disabled={!nav.hasNext && page === pageCount}
        loading={loading}
        iconId="ri-arrow-right-s-line"
        onClick={nav.next}
      >
        {t("Suivant")}
      </Button>
    </div>
  )
}

export default NavigationButtons
