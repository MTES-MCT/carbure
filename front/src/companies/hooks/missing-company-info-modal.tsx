import useEntity from "carbure/hooks/entity"
import { usePortal } from "common/components/portal"
import CompanyInfoMissingSirenDialog from "companies/components/company-info-siren-missing-dialog"
import { useEffect, useRef } from "react"


export const useMissingCompanyInfoModal = () => {
  const entity = useEntity()
  const functionCalled = useRef(false);
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
    portal((close) => (
      <CompanyInfoMissingSirenDialog onClose={close} />
    ))
  }

  useEffect(() => {

    if (!entity.registration_id && !functionCalled.current && (isCPO || isAirline || isOperator || isTrader || isProducer || isPowerOrHeatProducer)) {
      displayMissingCompanyInfoModal()
      functionCalled.current = true;
    }
  }, [])

  return
}

export default useMissingCompanyInfoModal
