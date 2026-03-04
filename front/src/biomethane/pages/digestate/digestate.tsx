import { getDigestate } from "./api"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { Production } from "./components/production"
import { SpreadingDistance } from "./components/spreading-distance"
import {
  DigestateValorizationMethods,
  SpreadingManagementMethods,
} from "../production/types"
import { Spreading } from "./components/spreading"
import { ContainerFluid, LoaderOverlay } from "common/components/scaffold"
import { Composting } from "./components/composting"
import { IncinerationLandfill } from "./components/incineration-landfill"
import { Sale } from "./components/sale"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { SectionsManagerProvider } from "common/providers/sections-manager.provider"
import {
  MissingFields,
  useMissingFields,
} from "biomethane/components/missing-fields"
import { FormContext, useForm } from "common/components/form2"
import { BiomethaneDigestate } from "./types"
import { useContractProductionUnit } from "biomethane/providers/contract-production-unit"
import { useSelectedEntity } from "common/providers/selected-entity-provider"
import { useMemo } from "react"
import { Title } from "common/components/title"

const DigestatePage = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { selectedYear, isDeclarationInCurrentPeriod, annualDeclaration } =
    useAnnualDeclaration()
  const form = useForm<BiomethaneDigestate | undefined | object>(undefined)
  const { selectedEntityId } = useSelectedEntity()

  const { result: digestate, loading } = useQuery(getDigestate, {
    key: "digestate",
    params: [entity.id, selectedYear, selectedEntityId],
    onSuccess: (data) => {
      form.setValue(data?.data)
    },
    onError: () => {
      // If the digestate is not found, we need to set an empty object to the form
      form.setValue({})
    },
  })
  const { contractInfos: contract, productionUnit } =
    useContractProductionUnit()

  const displayConditionalSections = useMemo(() => {
    if (!productionUnit) return false

    // If the declaration year selected is not the current year and the declaration is not open, we don't display the conditional sections
    if (!isDeclarationInCurrentPeriod && !digestate) return false

    return true
  }, [productionUnit, isDeclarationInCurrentPeriod, digestate])

  usePrivateNavigation(t("Digestat"))
  useMissingFields(form)

  if (loading && !digestate) return <LoaderOverlay />

  return (
    <FormContext.Provider value={form}>
      <MissingFields />
      {displayConditionalSections && (
        <>
          {productionUnit && <Production productionUnit={productionUnit} />}

          {productionUnit?.digestate_valorization_methods?.includes(
            DigestateValorizationMethods.SPREADING
          ) && (
            <>
              <SpreadingDistance />
              <Spreading digestate={digestate?.data} />
            </>
          )}

          {productionUnit?.digestate_valorization_methods?.includes(
            DigestateValorizationMethods.COMPOSTING
          ) && <Composting />}

          {productionUnit?.digestate_valorization_methods?.includes(
            DigestateValorizationMethods.INCINERATION_LANDFILLING
          ) && <IncinerationLandfill contract={contract} />}

          {productionUnit?.spreading_management_methods?.includes(
            SpreadingManagementMethods.SALE
          ) && <Sale />}
        </>
      )}
      {annualDeclaration && !isDeclarationInCurrentPeriod && !digestate ? (
        <ContainerFluid>
          <Title is="h2" as="h5">
            {t(
              "Aucune donnée n'est à renseigner pour l'année {{year}} sur la page Digestat.",
              {
                year: selectedYear,
              }
            )}
          </Title>
        </ContainerFluid>
      ) : null}
    </FormContext.Provider>
  )
}

export const Digestate = () => {
  return (
    <SectionsManagerProvider>
      <DigestatePage />
    </SectionsManagerProvider>
  )
}
