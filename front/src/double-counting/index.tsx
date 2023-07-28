import { useState } from "react"
import { Route, Routes, Navigate, useLocation } from "react-router-dom"
import { useTranslation } from "react-i18next"
import useEntity from "carbure/hooks/entity"
import { useQuery } from "common/hooks/async"
import { Col, Main, Row } from "common/components/scaffold"
import Select from "common/components/select"
import ApplicationList from "./components/application-list"
import QuotasList from "./components/dc-quotas"
import * as api from "./api"
import useTitle from "common/hooks/title"
import Tabs from "common/components/tabs"
import DoubleCountingFilesChecker from "./components/files-checker"
import { Loader } from "common/components/icons"
import { AgreementsSnapshot, ApplicationSnapshot } from "./types"

const DoubleCounting = () => {
  const { t } = useTranslation()
  useTitle(t("Double comptage"))

  const entity = useEntity()
  const location = useLocation()

  const snapshotResponse = useQuery(api.getSnapshot, {
    key: "operator-snapshot",
    params: [entity.id],
  })
  const snapshot = snapshotResponse.result?.data.data

  console.log('snapshotData:', snapshot)

  return (
    <Main>
      {!location.pathname.includes("/files-checker") && (
        <header>

          <section>
            <Tabs
              variant="main"
              tabs={[
                {
                  key: "applications", path: "applications", label:
                    <Row>
                      <Col>
                        <p>
                          {snapshotResponse.loading ? (
                            <Loader size={20} />
                          ) : snapshot?.applications_pending
                          }
                        </p>
                        <strong>
                          {t("Dossiers en cours")}
                        </strong>
                      </Col>
                    </Row>
                },
                {
                  key: "quotas", path: "quotas", label:
                    <Row><Col>
                      <p>
                        {snapshotResponse.loading ? (
                          <Loader size={20} />
                        ) : snapshot?.agreements_active
                        }
                      </p>
                      <strong>
                        {t("Agréments actifs")}
                      </strong>
                    </Col>
                    </Row>
                }]}
            />
          </section>
        </header>
      )}
      <Routes>
        <Route
          path="applications"
          element={<ApplicationList entity={entity} snapshot={snapshot as ApplicationSnapshot} />}
        />
        <Route path="quotas" element={<QuotasList snapshot={snapshot as AgreementsSnapshot} />} />
        <Route
          path="files-checker/*"
          element={<DoubleCountingFilesChecker />}
        />
        <Route path="*" element={<Navigate to="applications" />} />
      </Routes>
    </Main>
  )
}

export default DoubleCounting
