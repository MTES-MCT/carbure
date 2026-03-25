import { DigestateProcessing } from "./components/digestate-processing"
import { DigestateStorage } from "./components/digestate-storage/digestate-storage"
import { GeneralInfo } from "./components/general-info"
import { ICPE } from "./components/icpe"
import { ProductionSite } from "./components/production-site"
import { SanitaryAgreement } from "./components/sanitary-agreement"
import { useProductionUnit } from "./production.hooks"
import { AnnualDeclarationAlert } from "biomethane/components/annual-declaration-alert"
import { WatchedFieldsProvider } from "biomethane/providers/watched-fields"
import { getProductionUnitWatchedFields } from "./api"
import { LoaderOverlay } from "common/components/scaffold"
import { ProductionUnitForm } from "./types"
import { FormContext, useForm } from "common/components/form2"
import { useMissingFields } from "biomethane/components/missing-fields"
import { SectionsManagerProvider } from "common/providers/sections-manager.provider"

export const BiomethaneProductionPageContent = () => {
  const form = useForm<ProductionUnitForm>({})
  const { result: productionUnit, loading } = useProductionUnit({
    onSuccess: (productionUnit) => {
      form.setValue(productionUnit ?? {})
    },
    onError: () => {
      form.setValue({})
    },
  })

  useMissingFields(form)

  if (loading) return <LoaderOverlay />

  return (
    <FormContext.Provider value={form}>
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
    </FormContext.Provider>
  )
}

export const BiomethaneProductionPage = () => (
  <SectionsManagerProvider>
    <BiomethaneProductionPageContent />
  </SectionsManagerProvider>
)
