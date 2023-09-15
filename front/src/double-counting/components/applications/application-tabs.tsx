import { ProductionSiteDetails } from "carbure/types"
import Tabs from "common/components/tabs"
import { compact } from "common/utils/collection"
import { DoubleCountingProduction, DoubleCountingSourcing } from "double-counting/types"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { ProductionSiteForm } from "settings/components/production-site-dialog"
import { ProductionTable, SourcingFullTable } from "../dc-tables"



interface ApplicationDetailsProps {
    production?: DoubleCountingProduction[]
    sourcing?: DoubleCountingSourcing[]
    quotas?: Record<string, number>
    setQuotas?: (quotas: Record<string, number>) => void
    hasAgreement?: boolean
    productionSite?: ProductionSiteDetails
}

const ApplicationTabs = ({ productionSite, production, sourcing, quotas, setQuotas, hasAgreement }: ApplicationDetailsProps) => {
    const [focus, setFocus] = useState(productionSite ? "production_site" : "sourcing_forecast")
    const { t } = useTranslation()

    return <>
        <section>
            <Tabs
                variant="switcher"
                tabs={compact([
                    productionSite && {
                        key: "production_site",
                        label: t("Site de production")
                    },
                    {
                        key: "sourcing_forecast",
                        label: t("Approvisionnement"),
                    },
                    {
                        key: "production",
                        label: t("Production"),
                    }

                ])}
                focus={focus}
                onFocus={setFocus}
            />

        </section>
        {focus === "production_site" && productionSite &&
            <section>
                <ProductionSiteForm
                    readOnly
                    productionSite={productionSite} />
            </section>
        }


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