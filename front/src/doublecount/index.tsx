import { useEffect } from 'react'
import * as api from './api'
import { Main } from 'common/components'
import useAPI from 'common/hooks/use-api'
import AgreementList from './components/agreement-list'

const DoubleCounting = () => {
  const [agreements, getAgreements] = useAPI(api.getAllDoubleCountingAgreements)
  
  useEffect(() => {
    getAgreements()
  }, [getAgreements])

  return (
    <Main>
      <AgreementList agreements={agreements.data} />
    </Main>
  )
}

export default DoubleCounting