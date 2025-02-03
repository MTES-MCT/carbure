import useEntity from "carbure/hooks/entity"
import { Main } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import useTitle from "common/hooks/title"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import * as api from "./api"
import AgreementList from "./components/agreements/agreement-list"
import ApplicationList from "./components/applications/application-list"
import DoubleCountingFilesChecker from "./components/files-checker"

const DoubleCounting = () => {
  const { t } = useTranslation()
  useTitle(t("Double comptage"))

  const entity = useEntity()

  const snapshotResponse = useQuery(api.getSnapshot, {
    key: "dc-snapshot",
    params: [entity.id],
  })
  const snapshot = snapshotResponse.result?.data

  return (
    <Main>
      <Routes>
        <Route
          path="applications"
          element={<ApplicationList snapshot={snapshot} />}
        />

        <Route
          path="agreements"
          element={<AgreementList snapshot={snapshot} />}
        />
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
