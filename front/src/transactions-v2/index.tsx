import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useAsync } from 'react-async-hook'

import useEntity from 'carbure/hooks/entity' 
import { Main } from 'common-v2/components/scaffold'
import { Select } from 'common-v2/components/select'
import * as api from './api'

export const Transactions = () => {
  const { t } = useTranslation()

  const entity = useEntity()
  const [year, setYear] = useState<number | undefined>()

  const snapshot = useAsync(api.getSnapshot, [entity.id, year ?? 2021])

  return (
    <Main>
      <header>
        <section>
          <h1>{t("Transactions")}</h1>

          <Select 
            variant="inline"
            placeholder={t("Choisir une année")}
            value={year} 
            onChange={setYear}
            options={[2019, 2020, 2021]}
          />
        </section> 

        <section>
        </section>
      </header>

    </Main>
  )
}

export default Transactions