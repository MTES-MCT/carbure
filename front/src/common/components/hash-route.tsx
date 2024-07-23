import { matchPath, useLocation, useMatch } from "react-router-dom"

interface HashRouteProps {
	path: string
	element?: React.ReactNode
}

export const HashRoute = ({ path, element }: HashRouteProps) => {
	const match = useHashMatch(path)
	return match && <>{element}</>
}

export const useHashMatch: typeof useMatch = (pattern) => {
	const location = useLocation()
	return matchPath(`/${pattern}`, location.hash.replace("#", "/"))
}

export default HashRoute
