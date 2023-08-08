import useEntity from "carbure/hooks/entity"
import { Loader } from "common/components/icons"
import { Col, Main, Row } from "common/components/scaffold"
import Tabs from "common/components/tabs"
import { useQuery } from "common/hooks/async"
import useTitle from "common/hooks/title"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes, useLocation } from "react-router-dom"
import * as api from "./api"
import AgreementList from "./components/agreement-list"
import ApplicationList from "./components/application-list"
import DoubleCountingFilesChecker from "./components/files-checker"
import { DoubleCountingAgreementsSnapshot, DoubleCountingApplicationSnapshot } from "./types"


const DoubleCounting = () => {
  const { t } = useTranslation()
  useTitle(t("Double comptage"))

  const entity = useEntity()
  const location = useLocation()

  const snapshotResponse = useQuery(api.getSnapshot, {
    key: "dc-snapshot",
    params: [entity.id],
  })
  const snapshot = snapshotResponse.result?.data.data


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
                          {t("Dossiers en attente", {
                            count: snapshot?.applications_pending,
                          })}
                        </strong>
                      </Col>
                    </Row>
                },
                {
                  key: "agreements", path: "agreements", label:
                    <Row><Col>
                      <p>
                        {snapshotResponse.loading ? (
                          <Loader size={20} />
                        ) : snapshot?.agreements_active
                        }
                      </p>
                      <strong>
                        {t("Agréments actifs", {
                          count: snapshot?.agreements_active,
                        })}
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
          element={<ApplicationList entity={entity} snapshot={snapshot as DoubleCountingApplicationSnapshot} />}
        />

        <Route path="agreements" element={<AgreementList snapshot={snapshot as DoubleCountingAgreementsSnapshot} />} />
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
