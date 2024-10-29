import { useLocation, useNavigate } from "react-router-dom"
import { useHashMatch } from "../hash-route"
import { useCallback, useEffect } from "react"
import { getNeighborsInfos } from "./navigation.utils"

/**
 * @param map a map with a pair key(the page)/value(array of ids)
 * @returns An array containing all ids
 */
const mapToNeighbors = (map: Map<number, number[]>) =>
  [...map.entries()].sort((a, b) => a[0] - b[0]).flatMap(([, values]) => values)

/**
 * Return an array of booleans to know if the current id has next/previous id
 * @param idsMap a map with a pair key(the page)/value(array of ids)
 * @param currentPage the page related to the current id
 * @param pageCount
 * @returns
 */
export function useNavigation(
  idsMap: Map<number, number[]>,
  currentPage: number,
  pageCount: number
) {
  const navigate = useNavigate()
  const location = useLocation()

  const match = useHashMatch(":root/:id")
  const root = match?.params.root
  const current = parseInt(match?.params.id ?? "")
  const neighbors = mapToNeighbors(idsMap)

  const {
    index,
    isOut,
    hasPrev,
    hasNext,
    hasPrevCurrentPage,
    hasNextCurrentPage,
  } = getNeighborsInfos(idsMap, current, currentPage, pageCount)

  const prev = useCallback(() => {
    if (hasPrev && neighbors[index - 1]) {
      const searchParams = new URLSearchParams(location.search)

      const searchParamPage = searchParams.get("page")

      // Update page query param when the current id is the last id of the current page
      if (!hasPrevCurrentPage && searchParamPage) {
        const prevPage = parseInt(searchParamPage) - 1

        if (prevPage === 1) searchParams.delete("page")
        else searchParams.set("page", prevPage.toString())
      }

      navigate({
        pathname: location.pathname,
        search: `?${searchParams.toString()}`,
        hash: `${root}/${neighbors[index - 1]}`,
      })
    }
  }, [neighbors, root, hasPrev, index, navigate, location, hasPrevCurrentPage])

  const next = useCallback(() => {
    const searchParams = new URLSearchParams(location.search)
    const searchParamPage = parseInt(searchParams.get("page") ?? "1")

    if (isOut && neighbors[0]) {
      // Remove page param to restart page
      searchParams.delete("page")
      navigate({
        pathname: location.pathname,
        search: `?${searchParams.toString()}`,
        hash: `${root}/${neighbors[0]}`,
      })
    } else if (hasNext && neighbors[index + 1]) {
      // Change page query param when the next id is on a new page
      if (!hasNextCurrentPage) {
        searchParams.set("page", `${searchParamPage + 1}`)
      }
      navigate({
        pathname: location.pathname,
        search: `?${searchParams.toString()}`,
        hash: `${root}/${neighbors[index + 1]}`,
      })
    }
  }, [
    neighbors,
    root,
    hasNext,
    isOut,
    index,
    navigate,
    location,
    hasNextCurrentPage,
  ])

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if ((e.target as Element)?.matches("input")) {
        return
      }

      if (e.key === "ArrowLeft") {
        prev()
      } else if (e.key === "ArrowRight") {
        next()
      }
    }

    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [prev, next])

  return {
    index,
    isOut,
    hasPrev,
    hasNext,
    hasPrevCurrentPage,
    hasNextCurrentPage,
    prev,
    next,
  }
}
