import { Fragment } from "react"
import { DigestateProcessing } from "./components/digestate-processing"
import { DigestateStorage } from "./components/digestate-storage/digestate-storage"
import { GeneralInfo } from "./components/general-info"
import { ICPE } from "./components/icpe"
import { ProductionSite } from "./components/production-site"
import { SanitaryAgreement } from "./components/sanitary-agreement"
import { useProductionUnit } from "./production.hooks"

export const BiomethaneProductionPage = () => {
  const { result: productionUnit } = useProductionUnit()

  return (
    <Fragment key={productionUnit?.id}>
      <GeneralInfo productionUnit={productionUnit} />
      <SanitaryAgreement productionUnit={productionUnit} />
      <ICPE productionUnit={productionUnit} />
      <ProductionSite productionUnit={productionUnit} />
      <DigestateProcessing productionUnit={productionUnit} />
      <DigestateStorage />
    </Fragment>
  )
}
