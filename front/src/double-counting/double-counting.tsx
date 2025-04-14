import { Button } from "common/components/button2"
import { Content, Main } from "common/components/scaffold"
import { Tabs } from "common/components/tabs2"
import { useRights } from "common/hooks/entity"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes, useNavigate } from "react-router-dom"
import { UserRole } from "common/types"
import { Table } from "common/components/table2"
import {
  DoubleCountingTab,
  useDoubleCounting,
  useDoubleCountingColumns,
} from "./double-counting.hooks"
import { NoResult } from "common/components/no-result2"
import {
  DoubleCountingApplicationOverview,
  DoubleCountingStatus,
} from "./types"
import HashRoute from "common/components/hash-route"
import { ApplicationDetailsDialog } from "./components/application-details-dialog"
import { AgreementDetailsDialog } from "./components/agreement-details-dialog"
import { usePortal } from "common/components/portal"
import DoubleCountingUploadDialog from "./components/upload-dialog"

const DoubleCounting = () => {
  const { t } = useTranslation()
  usePrivateNavigation(t("Agréments double comptage"))
  const { tab, setTab, applications, loading } = useDoubleCounting()
  const columns = useDoubleCountingColumns()
  const rights = useRights()
  const navigate = useNavigate()
  const portal = usePortal()
  const canModify = rights.is(UserRole.Admin, UserRole.ReadWrite)

  function showApplicationDialog(
    application: DoubleCountingApplicationOverview
  ) {
    if (
      [
        DoubleCountingStatus.PENDING,
        DoubleCountingStatus.INPROGRESS,
        DoubleCountingStatus.REJECTED,
      ].includes(application.status)
    ) {
      navigate({
        pathname: location.pathname,
        hash: `double-counting/applications/${application.id}`,
      })
    } else {
      navigate({
        pathname: location.pathname,
        hash: `double-counting/agreements/${application.agreement_id}`,
      })
    }
  }

  function showUploadDialog() {
    portal((resolve) => <DoubleCountingUploadDialog onClose={resolve} />)
  }
  return (
    <Main>
      <header>
        <Button
          iconId="ri-add-line"
          asideX
          disabled={!canModify}
          onClick={showUploadDialog}
        >
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
            icon: "ri-draft-line",
            iconActive: "ri-draft-fill",
          },
          {
            key: DoubleCountingTab.PENDING,
            path: DoubleCountingTab.PENDING,
            label: t("En attente"),
            icon: "ri-pause-circle-line",
            iconActive: "ri-pause-circle-fill",
          },
          {
            key: DoubleCountingTab.EXPIRED,
            path: DoubleCountingTab.EXPIRED,
            label: t("Expirés"),
            icon: "ri-chat-history-line",
            iconActive: "ri-chat-history-fill",
          },
          {
            key: DoubleCountingTab.REJECTED,
            path: DoubleCountingTab.REJECTED,
            label: t("Rejetés"),
            icon: "ri-close-line",
            iconActive: "ri-close-fill",
          },
        ]}
        sticky
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
                  onAction={showApplicationDialog}
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
      <HashRoute
        path="double-counting/applications/:id"
        element={<ApplicationDetailsDialog />}
      />
      <HashRoute
        path="double-counting/agreements/:id"
        element={<AgreementDetailsDialog />}
      />
    </Main>
  )
}

export default DoubleCounting
