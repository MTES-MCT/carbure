import { useLocation } from "react-router"
import { Page } from "../missing-fields.constants"

export const usePageDetection = () => {
  const location = useLocation()

  const isDigestatePage = location.pathname.includes(Page.DIGESTATE)
  const isEnergyPage = location.pathname.includes(Page.ENERGY)
  const currentPage = isDigestatePage
    ? Page.DIGESTATE
    : isEnergyPage
      ? Page.ENERGY
      : undefined

  return {
    isDigestatePage,
    isEnergyPage,
    currentPage,
  }
}
