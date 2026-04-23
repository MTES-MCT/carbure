import { useProductionUnit } from "biomethane/pages/production/production.hooks"

export const useBiomethaneProductionUnit = () => {
  const { result: productionUnit, loading: loadingProductionUnit } =
    useProductionUnit()

  return { productionUnit, loadingProductionUnit }
}
