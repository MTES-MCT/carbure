import useEntity from "carbure/hooks/entity"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import { useQuery } from "common/hooks/async"
import useYears from "common/hooks/years"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import { Loader } from "common/components/icons"
import Tabs from "common/components/tabs"
import { formatNumber } from "common/utils/formatters"
import * as api from "./api"
import { ElecSnapshot } from "./types"



const defaultElecSnapshot: ElecSnapshot = {
  provisioned_energy: 0,
  remaining_energy: 0,
  provision_cert_available: 0,
  provision_cert_history: 0,
  transferred_energy: 0,
  transfer_certificates_pending: 0,
  transfer_certificates_accepted: 0,
  transfer_certificates_rejected: 0,
}

export const Elec = () => {
  const { t } = useTranslation()

  const entity = useEntity()

  const years = useYears("elec", api.getYears)
  console.log('years:', years)
  const snapshotResponse = useQuery(api.getSnapshot, {
    key: "elec-snapshot",
    params: [entity.id, years.selected],
  })

  const snapshot = snapshotResponse.result?.data.data ?? defaultElecSnapshot
  console.log('snapshot:', snapshot)


  // const snapshot = elecAdminSnapshot ?? defaultElecAdminSnapshot //TODO TEST with testing data

  return (

    <Main>
      <header>
        <section>
          <h1>{t("Électricité")}</h1>

          <Select
            loading={years.loading}
            variant="inline"
            placeholder={t("Choisir une année")}
            value={years.selected}
            onChange={years.setYear}
            options={years.options}
            sort={(year) => -year.value}
          />
        </section>

        <section>
          {/* <ElecAdminTabs loading={snapshotResponse.loading} snapshot={snapshot} /> */}
        </section>
      </header>


      <Routes>
        {/* <Route
          path="provision/*"
          element={
            <ProvisionList snapshot={snapshot} year={years.selected} />
          }
        /> */}


        {/* <Route
          path="*"
          element={
            <Navigate
              replace
              to={`provision/${ElecAdminProvisionCertificateStatus.Available.toLocaleLowerCase()}`}
            />
          }
        /> */}

      </Routes>
    </Main>


  )
}

export default Elec



// interface ElecAdminTabsProps {
//   loading: boolean
//   snapshot: ElecAdminSnapshot
// }


// function ElecAdminTabs({
//   loading,
//   snapshot
// }: ElecAdminTabsProps) {
//   const { t } = useTranslation()

//   return (<Tabs variant="main" tabs={[{
//     key: "provision",
//     path: "provision",
//     label: <>
//       <p style={{
//         fontWeight: "normal"
//       }}>
//         {loading ? <Loader size={20} /> : snapshot?.provision_certificates}
//         {/* {loading ? <Loader size={20} /> : formatNumber(snapshot?.provisioned_energy)} MWh */}
//       </p>
//       <strong>
//         {/* {t("Énergie attribuée")} */}
//         {t("Certificats de founiture")}
//       </strong>
//     </>
//   }, {
//     key: "transfer",
//     path: "transfer",
//     label: <>
//       <p style={{
//         fontWeight: "normal"
//       }}>
//         {loading ? <Loader size={20} /> : snapshot?.transfer_certificates}
//         {/* {loading ? <Loader size={20} /> : formatNumber(snapshot?.transferred_energy)} MWh */}
//       </p>
//       <strong>
//         {t("Énergie cédée")}
//         {/* {t("Énergie cédée")} */}
//       </strong>
//     </>
//   }]} />);
// }


