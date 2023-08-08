import Tabs from "common/components/tabs"
import { DoubleCountingProduction, DoubleCountingSourcing } from "double-counting/types"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { ProductionTable, SourcingFullTable } from "./dc-tables"



interface ApplicationDetailsProps {
    production?: DoubleCountingProduction[]
    sourcing?: DoubleCountingSourcing[]
    quotas?: Record<string, number>
    setQuotas?: (quotas: Record<string, number>) => void
    hasAgreement?: boolean
}

const ApplicationTabs = ({ production, sourcing, quotas, setQuotas, hasAgreement }: ApplicationDetailsProps) => {
    const [focus, setFocus] = useState("production")
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
                    sourcing={sourcing ?? []}
                />
            </section>
        }


        {focus === "production" &&
            <section>
                <ProductionTable
                    production={production ?? []}
                    quotas={quotas ?? {}}
                    setQuotas={setQuotas}
                    hasAgreement={hasAgreement}
                />
            </section>
        }
    </>
}
export default ApplicationTabs