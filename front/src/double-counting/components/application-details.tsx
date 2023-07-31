import Tabs from "common/components/tabs"
import { DoubleCountingFileInfo } from "double-counting/types"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { ProductionTable, SourcingFullTable } from "./dc-tables"

const ApplicationDetails = ({ fileData }: { fileData: DoubleCountingFileInfo }) => {
    const [focus, setFocus] = useState("sourcing_forecast")
    const { t } = useTranslation()

    return <>
        <section>
            <Tabs
                variant="switcher"
                tabs={[
                    {
                        key: "sourcing_forecast",
                        label: t("Approvisionnement"),
                    },
                    {
                        key: "production",
                        label: t("Production"),
                    }

                ]}
                focus={focus}
                onFocus={setFocus}
            />

        </section>

        {focus === "sourcing_forecast" &&
            <section>
                <SourcingFullTable
                    sourcing={fileData.sourcing ?? []}
                />
            </section>
        }


        {focus === "production" &&
            <section>
                <ProductionTable
                    production={fileData.production ?? []}
                />
            </section>
        }
    </>
}
export default ApplicationDetails