import { ActionBar } from "common/components/scaffold"
import Tabs from "common/components/tabs"
import { ElecAdminSnapshot } from "elec-admin/types"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import ProvisionImporButton from "./provisionImportButton"

type ProvisionListProps = {
    snapshot: ElecAdminSnapshot
}

const ProvisionList = ({ snapshot }: ProvisionListProps) => {
    const { t } = useTranslation()
    const [tab, setTab] = useState("available")

    return (
        <>
            {/* <FileArea
            icon={Upload}
            label={t("Importer le fichier\nsur la plateforme")}
            onChange={(file) => file && importCertificates.execute(entity.id, file)}
        > */}
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

                    <ProvisionImporButton />
                </ActionBar>
            </section >


            {/* </FileArea > */}
        </>
    )
}
export default ProvisionList


