import { ActionBar } from "common/components/scaffold"
import Tabs from "common/components/tabs"
import { ElecAdminProvisionCertificateStatus, ElecAdminSnapshot } from "elec-admin/types"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import ProvisionImporButton from "./provisionImportButton"
import { useQuery } from "common/hooks/async"
import * as api from "../api"
import useEntity from "carbure/hooks/entity"
import { useProvistionCertificateQueryParamsStore } from "elec-admin/hooks/provision-certificate-query-params-store"
import { useProvisionCertificatesQuery } from "elec-admin/hooks/provision-certificates-query"
import ElecAdmin from "elec-admin"
import { useMatch } from "react-router-dom"
import { StatusSwitcher } from "./provisionStatusSwitch"

type ProvisionListProps = {
    snapshot: ElecAdminSnapshot
    year: number
}

const ProvisionList = ({ snapshot, year }: ProvisionListProps) => {
    const { t } = useTranslation()
    const entity = useEntity()
    const status = useAutoStatus()
    const [state, actions] = useProvistionCertificateQueryParamsStore(entity, year, status, snapshot)
    const query = useProvisionCertificatesQuery(state)
    console.log('query:', query)

    const provisionCertificatesResponse = useQuery(api.getProvisionCertificates, {
        key: "provision-certificates",
        params: [query],
    })

    const provisionCertificates = provisionCertificatesResponse.result?.data.data
    console.log('provisionCertificates:', provisionCertificates)

    return (
        <>
            {/* <FileArea
            icon={Upload}
            label={t("Importer le fichier\nsur la plateforme")}
            onChange={(file) => file && importCertificates.execute(entity.id, file)}
        > */}
            <section>
                <ActionBar>

                    <StatusSwitcher
                        status={status}
                        onSwitch={actions.setStatus}
                        snapshot={snapshot}
                    />

                    <ProvisionImporButton />
                </ActionBar>
            </section >


            {/* </FileArea > */}
        </>
    )
}
export default ProvisionList




export function useAutoStatus() {
    const matchStatus = useMatch("/org/:entity/elec-admin/:year/:status/*")
    const status = matchStatus?.params?.status?.toUpperCase() as ElecAdminProvisionCertificateStatus
    return status ?? ElecAdminProvisionCertificateStatus.Available
}