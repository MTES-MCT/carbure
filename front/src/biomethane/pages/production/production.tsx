import { DigestateProcessing } from "./components/digestate-processing/digestate-processing"
import { DigestateStorage } from "./components/digestate-storage/digestate-storage"
import { GeneralInfo } from "./components/general-info/general-info"
import { ICPE } from "./components/icpe/icpe"
import { ProductionSite } from "./components/production-site/production-site"
import { SanitaryAgreement } from "./components/sanitary-agreement/sanitary-agreement"
import { useProductionUnit } from "./production.hooks"

export const BiomethaneProductionPage = () => {
  const { result: productionUnit } = useProductionUnit()

  if (!productionUnit) return null

  return (
    <>
      <GeneralInfo productionUnit={productionUnit} />
      <SanitaryAgreement productionUnit={productionUnit} />
      <ICPE productionUnit={productionUnit} />
      <ProductionSite />
      <DigestateProcessing />
      <DigestateStorage />
    </>
  )
}
