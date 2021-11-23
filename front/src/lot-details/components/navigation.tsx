import { useCallback, useEffect } from "react"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate, useParams } from "react-router-dom"
import Button from "common-v2/components/button"
import { ChevronLeft, ChevronRight } from "common-v2/components/icons"
import { useStatus } from "transactions-v2/components/status"

export interface NavigationProps {
  neighbors: number[]
}

export const NavigationButtons = ({ neighbors }: NavigationProps) => {
  const { t } = useTranslation()
  const nav = useNavigation(neighbors)

  return (
    <>
      <Button
        asideX
        disabled={!nav.hasPrev}
        icon={ChevronLeft}
        label={t("Lot précédent")}
        action={nav.prev}
      />
      <Button
        disabled={!nav.hasNext}
        icon={ChevronRight}
        label={t("Lot suivant")}
        action={nav.next}
      />
    </>
  )
}

export function useNavigation(neighbors: number[]) {
  const navigate = useNavigate()
  const location = useLocation()

  const status = useStatus()
  const params = useParams<"id">()
  const current = parseInt(params.id ?? "")

  const index = neighbors.indexOf(current)
  const total = neighbors.length

  const isOut = index < 0
  const hasPrev = index > 0
  const hasNext = index < neighbors.length - 1

  const prev = useCallback(() => {
    if (hasPrev) {
      navigate({
        pathname: `../${status}/${neighbors[index - 1]}`,
        search: location.search,
      })
    }
  }, [neighbors, status, hasPrev, index, navigate, location])

  const next = useCallback(() => {
    if (isOut) {
      navigate({
        pathname: `${neighbors[0]}`,
        search: location.search,
      })
    } else if (hasNext) {
      navigate({
        pathname: `../${status}/${neighbors[index + 1]}`,
        search: location.search,
      })
    }
  }, [neighbors, status, hasNext, isOut, index, navigate, location])

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
    total,
    isOut,
    hasPrev,
    hasNext,
    prev,
    next,
  }
}

export default NavigationButtons
