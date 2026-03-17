import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { useRoutes } from "common/hooks/routes"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"

const dataIsNullOrHasErrors = (data: string[] | null | undefined) => {
  return data === null || (data && data.length > 0)
}

export type SettingsErrorItem = {
  route: string
  errors: string[]
  name: string
}

export const useSettingsNotFilled = () => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const { annualDeclaration } = useAnnualDeclaration()

  const routeMissingObject = useMemo(() => {
    const contractMissingFields =
      annualDeclaration?.missing_fields?.contract_missing_fields
    const productionUnitMissingFields =
      annualDeclaration?.missing_fields?.production_unit_missing_fields ?? null
    const injectionMissingFields =
      annualDeclaration?.missing_fields?.injection_missing_fields ?? null

    if (dataIsNullOrHasErrors(contractMissingFields)) {
      return routes.SETTINGS.BIOMETHANE.CONTRACT
    }
    if (dataIsNullOrHasErrors(productionUnitMissingFields)) {
      return routes.SETTINGS.BIOMETHANE.PRODUCTION
    }
    if (dataIsNullOrHasErrors(injectionMissingFields)) {
      return routes.SETTINGS.BIOMETHANE.INJECTION
    }

    return routes.SETTINGS.BIOMETHANE.CONTRACT
  }, [
    annualDeclaration?.missing_fields?.contract_missing_fields,
    annualDeclaration?.missing_fields?.production_unit_missing_fields,
    annualDeclaration?.missing_fields?.injection_missing_fields,
    routes.SETTINGS.BIOMETHANE.CONTRACT,
    routes.SETTINGS.BIOMETHANE.PRODUCTION,
    routes.SETTINGS.BIOMETHANE.INJECTION,
  ])

  const errorsMapping = useMemo((): SettingsErrorItem[] => {
    const errors: SettingsErrorItem[] = []
    const contractMissingFields =
      annualDeclaration?.missing_fields?.contract_missing_fields
    const productionUnitMissingFields =
      annualDeclaration?.missing_fields?.production_unit_missing_fields
    const injectionMissingFields =
      annualDeclaration?.missing_fields?.injection_missing_fields

    if (contractMissingFields && contractMissingFields.length > 0) {
      errors.push({
        route: routes.SETTINGS.BIOMETHANE.CONTRACT,
        errors: contractMissingFields,
        name: t("Contrat"),
      })
    }

    if (productionUnitMissingFields && productionUnitMissingFields.length > 0) {
      errors.push({
        route: routes.SETTINGS.BIOMETHANE.PRODUCTION,
        errors: productionUnitMissingFields,
        name: t("Site de production"),
      })
    }

    if (injectionMissingFields && injectionMissingFields.length > 0) {
      errors.push({
        route: routes.SETTINGS.BIOMETHANE.INJECTION,
        errors: injectionMissingFields,
        name: t("Site d'injection"),
      })
    }

    return errors
  }, [
    annualDeclaration?.missing_fields?.contract_missing_fields,
    annualDeclaration?.missing_fields?.production_unit_missing_fields,
    annualDeclaration?.missing_fields?.injection_missing_fields,
    t,
    routes.SETTINGS.BIOMETHANE.CONTRACT,
    routes.SETTINGS.BIOMETHANE.PRODUCTION,
    routes.SETTINGS.BIOMETHANE.INJECTION,
  ])

  return { routeMissingObject, errorsMapping }
}
