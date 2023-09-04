import useEntity from "carbure/hooks/entity"
import HashRoute from "common/components/hash-route"
import NoResult from "common/components/no-result"
import { ActionBar } from "common/components/scaffold"
import Table, { Cell, Column } from "common/components/table"
import Tabs from "common/components/tabs"
import { useQuery } from "common/hooks/async"
import { formatDate } from "common/utils/formatters"
import { Fragment, useState } from "react"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "../api"
import { ElecAdminSnapshot } from "elec-admin/types"

type ProvisionListProps = {
    snapshot: ElecAdminSnapshot
}

const ProvisionList = ({ snapshot }: ProvisionListProps) => {
    const { t } = useTranslation()
    const [tab, setTab] = useState("available")

    return (<>
        <section>
            <ActionBar>
                <Tabs
                    focus={tab}
                    variant="switcher"
                    onFocus={setTab}
                    tabs={[
                        { key: "available", label: t("Disponible ({{count}})", { count: snapshot?.provision_certificates }) },
                        {
                            key: "history", label: t("Historique ({{ count }})",
                                { count: snapshot.transfer_certificates }
                            )
                        },
                    ]}
                />

            </ActionBar>
        </section >
    </>
    )
}
export default ProvisionList 