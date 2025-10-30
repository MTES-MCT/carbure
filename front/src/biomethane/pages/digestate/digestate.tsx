import { getDigestate } from "./api"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { Production } from "./components/production"
import { SpreadingDistance } from "./components/spreading-distance"
import { useProductionUnit } from "../production/production.hooks"
import {
  DigestateValorizationMethods,
  SpreadingManagementMethods,
} from "../production/types"
import { Spreading } from "./components/spreading"
import { LoaderOverlay } from "common/components/scaffold"
import { SettingsNotFilled } from "biomethane/layouts/settings-not-filled"
import { Composting } from "./components/composting"
import { IncinerationLandfill } from "./components/incineration-landfill"
import { Sale } from "./components/sale"
import { useGetContractInfos } from "../contract/contract.hooks"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { SectionsManagerProvider } from "common/providers/sections-manager.provider"
import { MissingFields } from "biomethane/components/missing-fields"
import { FormContext, useForm } from "common/components/form2"
import { BiomethaneDigestate } from "./types"
import { useMissingFields } from "biomethane/components/missing-fields/missing-fields.hooks"
import { BiomethanePageHeader } from "biomethane/layouts/page-header"

const DigestatePage = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { selectedYear } = useAnnualDeclaration()
  const form = useForm<BiomethaneDigestate | undefined | object>(undefined)

  const { result: digestate, loading } = useQuery(getDigestate, {
    key: "digestate",
    params: [entity.id, selectedYear],
    onSuccess: (data) => {
      form.setValue(data?.data)
    },
    onError: () => {
      // If the digestate is not found, we need to set an empty object to the form
      form.setValue({})
    },
  })

  const { result: productionUnit } = useProductionUnit()
  const { result: contract } = useGetContractInfos()

  usePrivateNavigation(t("Digestat"))
  useMissingFields(form)

  if (loading && !digestate) return <LoaderOverlay />

  if (!loading && !productionUnit?.id) {
    return <SettingsNotFilled />
  }

  return (
    <BiomethanePageHeader>
      <FormContext.Provider value={form}>
        <MissingFields />
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
      </FormContext.Provider>
    </BiomethanePageHeader>
  )
}

export const Digestate = () => {
  return (
    <SectionsManagerProvider>
      <DigestatePage />
    </SectionsManagerProvider>
  )
}
