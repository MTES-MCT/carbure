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

  const pageMap = [
    { test: isDigestatePage, page: Page.DIGESTATE },
    { test: isEnergyPage, page: Page.ENERGY },
    { test: isContractPage, page: Page.CONTRACT },
    { test: isProductionPage, page: Page.PRODUCTION },
    { test: isInjectionPage, page: Page.INJECTION },
  ]

  const currentPage = pageMap.find((p) => p.test)?.page

  return {
    isDigestatePage,
    isEnergyPage,
    isContractPage,
    isProductionPage,
    isInjectionPage,
    currentPage,
  }
}
