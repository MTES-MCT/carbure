import { DigestateProcessing } from "./components/digestate-processing"
import { DigestateStorage } from "./components/digestate-storage/digestate-storage"
import { GeneralInfo } from "./components/general-info"
import { ICPE } from "./components/icpe"
import { ProductionSite } from "./components/production-site"
import { SanitaryAgreement } from "./components/sanitary-agreement"
import { useProductionUnit } from "./production.hooks"
import { AnnualDeclarationAlert } from "biomethane/components/annual-declaration-alert"
import { WatchedFieldsProvider } from "biomethane/providers/watched-fields.provider"
import { getProductionUnitWatchedFields } from "./api"

export const BiomethaneProductionPage = () => {
  const { result: productionUnit } = useProductionUnit()

  return (
    <WatchedFieldsProvider
      apiFunction={getProductionUnitWatchedFields}
      queryKey="production-unit-watched-fields"
      key={productionUnit?.id}
    >
      <AnnualDeclarationAlert />
      <GeneralInfo productionUnit={productionUnit} />
      <SanitaryAgreement productionUnit={productionUnit} />
      <ICPE productionUnit={productionUnit} />
      <ProductionSite productionUnit={productionUnit} />
      <DigestateProcessing productionUnit={productionUnit} />
      <DigestateStorage />
    </WatchedFieldsProvider>
  )
}
