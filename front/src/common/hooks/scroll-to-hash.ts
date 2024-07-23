import { useEffect } from "react"
import { useLocation } from "react-router-dom"

const useScrollToHash = () => {
	const location = useLocation()

	useEffect(() => {
		const scrollToHash = () => {
			if (location.hash) {
				const element = document.getElementById(location.hash.substring(1))
				if (element) {
					element.scrollIntoView({ behavior: "smooth" })
				}
			}
		}

		scrollToHash()
	}, [location])

	return true
}

export default useScrollToHash
