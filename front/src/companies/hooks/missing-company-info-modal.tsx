import useEntity from "carbure/hooks/entity"
import { UserRole } from "carbure/types"
import { usePortal } from "common/components/portal"
import CompanyInfoMissingSirenDialog from "companies/components/company-info-siren-missing-dialog"
import { useEffect, useRef } from "react"

export const useMissingCompanyInfoModal = () => {
  const entity = useEntity()
  const functionCalled = useRef(false)
  const portal = usePortal()

  const {
    isTrader,
    isOperator,
    isProducer,
    isAirline,
    isCPO,
    isPowerOrHeatProducer,
  } = entity

  const displayMissingCompanyInfoModal = () => {
    portal((close) => <CompanyInfoMissingSirenDialog onClose={close} />)
  }

  useEffect(() => {
    if (
      !entity.registration_id &&
      !functionCalled.current &&
      (isCPO ||
        isAirline ||
        isOperator ||
        isTrader ||
        isProducer ||
        isPowerOrHeatProducer) &&
      entity.hasRights(UserRole.Admin, UserRole.ReadWrite)
    ) {
      displayMissingCompanyInfoModal()
      functionCalled.current = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return
}

export default useMissingCompanyInfoModal
