import { Fragment, useState,useEffect } from 'react'
import { Trans } from 'react-i18next'
import useAPI from 'common/hooks/use-api'
import { Route, Switch, Redirect } from 'common/components/relative-route'
import { Header, Main, Title, Box } from "common/components"
import { TabButton } from 'common/components/button'
import { Select } from 'common/components/select'
import { EntitySelection } from "carbure/hooks/use-entity"
import AgreementList from "./components/agreement-list"
import QuotasList from './components/dc-quotas'

import * as api from './api'

import styles from './index.module.css'

type DoubleCountingProps = {
  entity: EntitySelection
}

const DoubleCounting = ({ entity }: DoubleCountingProps) => {
  const [year, setYear] = useState(new Date().getFullYear())
  const [snapshot, getSnapshot] = useAPI(api.getDoubleCountingSnapshot)

  useEffect(() => {
    getSnapshot()
  }, [])

  return (
    <Fragment>
      <Header className={styles.doublecountHeader}>
        <Box row className={styles.doublecountTitle}>
          <Title>
            <Trans>Double comptage</Trans>
          </Title>

          <Select 
            level="inline"
            value={year}
            onChange={v => setYear(v as number)}
            className={styles.doublecountYears}
            options={snapshot.data?.years.map(year => ({ label: `${year}`, value: year }))}
          />
        </Box>

        <Box row className={styles.doublecountTabs}>
          <TabButton relative to="./agreements">
            <Trans>
              Dossiers
            </Trans>
          </TabButton>
          <TabButton relative to="./quotas">
            <Trans>
              Quotas
            </Trans>
          </TabButton>
        </Box>
      </Header>

      <Main className={styles.doublecountMain}>
        <Switch>
          <Route relative path="agreements">
            <AgreementList entity={entity} year={year} />
          </Route>

          <Route relative path="quotas">
            <QuotasList entity={entity} year={year} />
          </Route>

          <Redirect relative to="agreements" />
        </Switch>
      </Main>
    </Fragment>
  )
}

export default DoubleCounting
