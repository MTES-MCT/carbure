import { useEffect } from "react"

import { EntitySelection } from "../helpers/use-entity"
import { YearSelection } from "../query/use-year"

import * as api from "../../services/lots"
import useAPI from "../helpers/use-api"

// fetches current snapshot when parameters change
export default function useGetSnapshot(
  entity: EntitySelection,
  year: YearSelection
) {
  const [snapshot, resolveSnapshot] = useAPI(api.getSnapshot)

  const years = snapshot.data?.years

  // if the currently selected year is not in the list of available years
  // set it to the first available value
  if (years && !years.some((option) => option.value === year.selected)) {
    year.setYear(years[0].value as number)
  }

  function getSnapshot() {
    if (entity !== null) {
      return resolveSnapshot(entity.id, year.selected).cancel
    }
  }

  useEffect(getSnapshot, [resolveSnapshot, entity, year.selected])

  return { ...snapshot, getSnapshot }
}
