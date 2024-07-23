import { useCallback, useEffect } from "react"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import Button from "common/components/button"
import { ChevronLeft, ChevronRight, Return } from "common/components/icons"
import { useHashMatch } from "common/components/hash-route"
import { layout } from "common/components/scaffold"
import cl from "clsx"
import css from "./navigation.module.css"

export interface NavigationProps {
	neighbors: number[]
	closeAction?: () => void
}

export const NavigationButtons = ({
	neighbors,
	closeAction,
}: NavigationProps) => {
	const { t } = useTranslation()
	const nav = useNavigation(neighbors)

	return (
		<div data-asidex={true} className={cl(css.navigation)}>
			{neighbors.length > 1 && (
				<>
					<Button
						disabled={!nav.hasPrev}
						icon={ChevronLeft}
						label={t("Précédent")}
						action={nav.prev}
					/>
					<Button
						disabled={!nav.hasNext}
						icon={ChevronRight}
						label={t("Suivant")}
						action={nav.next}
					/>
				</>
			)}
			<Button icon={Return} label={t("Retour")} action={closeAction} />
		</div>
	)
}

export function useNavigation(neighbors: number[]) {
	const navigate = useNavigate()
	const location = useLocation()

	const match = useHashMatch(":root/:id")
	const root = match?.params.root
	const current = parseInt(match?.params.id ?? "")

	const index = neighbors.indexOf(current)
	const total = neighbors.length

	const isOut = index < 0
	const hasPrev = index > 0
	const hasNext = index < neighbors.length - 1

	const prev = useCallback(() => {
		if (hasPrev) {
			navigate({
				pathname: location.pathname,
				search: location.search,
				hash: `${root}/${neighbors[index - 1]}`,
			})
		}
	}, [neighbors, root, hasPrev, index, navigate, location])

	const next = useCallback(() => {
		if (isOut) {
			navigate({
				pathname: location.pathname,
				search: location.search,
				hash: `${root}/${neighbors[0]}`,
			})
		} else if (hasNext) {
			navigate({
				pathname: location.pathname,
				search: location.search,
				hash: `${root}/${neighbors[index + 1]}`,
			})
		}
	}, [neighbors, root, hasNext, isOut, index, navigate, location])

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
