import { Fragment, useState, useEffect } from "react"
import { Route, Routes, Navigate } from "react-router-dom"
import { Trans } from "react-i18next"
import useEntity from "carbure/hooks/entity"
import useAPI from "common/hooks/use-api"
import { Header, Main, Title, Box } from "common/components"
import { TabButton } from "common/components/button"
import { Select } from "common/components/select"
import AgreementList from "./components/agreement-list"
import QuotasList from "./components/dc-quotas"
import * as api from "./api"
import styles from "./index.module.css"

const DoubleCounting = () => {
  const entity = useEntity()

  const [year, setYear] = useState(new Date().getFullYear())
  const [snapshot, getSnapshot] = useAPI(api.getDoubleCountingSnapshot)

  useEffect(() => {
    getSnapshot()
  }, [getSnapshot])

  useEffect(() => {
    if (snapshot.data === null) return

    if (!snapshot.data.years.includes(year)) {
      setYear(snapshot.data.years[0])
    }
  }, [snapshot.data, year])

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
            onChange={(v) => setYear(v as number)}
            className={styles.doublecountYears}
            options={snapshot.data?.years.map((year) => ({
              label: `${year}`,
              value: year,
            }))}
          />
        </Box>

        <Box row className={styles.doublecountTabs}>
          <TabButton to="agreements">
            <Trans>Dossiers</Trans>
          </TabButton>
          <TabButton to="quotas">
            <Trans>Quotas</Trans>
          </TabButton>
        </Box>
      </Header>

      {/* prettier-ignore */}
      <Main className={styles.doublecountMain}>
        <Routes>
          <Route path="agreements" element={<AgreementList entity={entity} year={year} />} />
          <Route path="quotas" element={<QuotasList year={year} />} />
          <Route path="*" element={<Navigate to="agreements" />} />
        </Routes>
      </Main>
    </Fragment>
  )
}

export default DoubleCounting
