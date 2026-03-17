import { useLocation } from "react-router-dom"
import { Page } from "../missing-fields.constants"

export const usePageDetection = () => {
  const location = useLocation()
  const pathname = location.pathname

  const isDigestatePage = pathname.includes(Page.DIGESTATE)
  const isEnergyPage = pathname.includes(Page.ENERGY)
  const isContractPage = pathname.includes("biomethane/contract")
  const isProductionPage = pathname.includes("biomethane/production")
  const isInjectionPage = pathname.includes("biomethane/injection")

  const currentPage = isDigestatePage
    ? Page.DIGESTATE
    : isEnergyPage
      ? Page.ENERGY
      : isContractPage
        ? Page.CONTRACT
        : isProductionPage
          ? Page.PRODUCTION
          : isInjectionPage
            ? Page.INJECTION
            : undefined

  return {
    isDigestatePage,
    isEnergyPage,
    isContractPage,
    isProductionPage,
    isInjectionPage,
    currentPage,
  }
}
