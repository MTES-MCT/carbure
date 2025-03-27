import { Button } from "common/components/button2"
import { DraftFill, SendPlaneFill } from "common/components/icon"
import { Content, Main } from "common/components/scaffold"
import { Tabs } from "common/components/tabs2"
import { useRights } from "common/hooks/entity"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import { UserRole } from "common/types"
import { Table } from "common/components/table2"
import {
  DoubleCountingTab,
  useDoubleCounting,
  useDoubleCountingColumns,
} from "./double-counting.hooks"
import { NoResult } from "common/components/no-result2"

const DoubleCounting = () => {
  const { t } = useTranslation()
  usePrivateNavigation(t("Agréments double comptage"))
  const { tab, setTab, applications, loading } = useDoubleCounting()
  const columns = useDoubleCountingColumns()
  const rights = useRights()

  const canModify = rights.is(UserRole.Admin, UserRole.ReadWrite)

  return (
    <Main>
      <header>
        <Button iconId="ri-add-line" asideX disabled={!canModify}>
          {t("Envoyer une demande d'agrément")}
        </Button>
      </header>

      <Tabs
        keepSearch
        focus={tab}
        onFocus={setTab}
        tabs={[
          {
            key: DoubleCountingTab.ACTIVE,
            path: DoubleCountingTab.ACTIVE,
            label: t("Actifs"),
            icon: DraftFill,
          },
          {
            key: DoubleCountingTab.PENDING,
            path: DoubleCountingTab.PENDING,
            label: t("En attente"),
            icon: DraftFill,
          },
          {
            key: DoubleCountingTab.REJECTED_OR_EXPIRED,
            path: DoubleCountingTab.REJECTED_OR_EXPIRED,
            label: t("Expirés / Rejetés"),
            icon: SendPlaneFill,
          },
        ]}
      />
      <Content>
        <Routes>
          <Route
            path="/:status"
            element={
              !loading && applications.length === 0 ? (
                <NoResult />
              ) : (
                <Table
                  rows={applications}
                  onAction={() => {}}
                  columns={columns}
                  loading={loading}
                />
              )
            }
          />
          <Route
            path="*"
            element={<Navigate to={DoubleCountingTab.ACTIVE} />}
          />
        </Routes>
      </Content>
    </Main>
  )
}

export default DoubleCounting
