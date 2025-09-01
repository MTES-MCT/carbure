import { BiomethanePageHeader } from "biomethane/layouts/page-header"
import { useParams } from "react-router-dom"
import { getDigestate, getYears, validateDigestate } from "./api"
import useYears from "common/hooks/years-2"
import { useMutation, useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { Production } from "./components/production"
import { SpreadingDistance } from "./components/spreading-distance"
import { useProductionUnit } from "../production/production.hooks"
import {
  DigestateValorizationMethods,
  SpreadingManagementMethods,
} from "../production/types"
import { Spreading } from "./components/spreading"
import { DigestateProvider } from "./digestate.hooks"
import { LoaderOverlay } from "common/components/scaffold"
import { SettingsNotFilled } from "biomethane/layouts/settings-not-filled"
import { Composting } from "./components/composting"
import { IncinerationLandfill } from "./components/incineration-landfill"
import { Sale } from "./components/sale"
import { useGetContractInfos } from "../contract/contract.hooks"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"
import { useNotify } from "common/components/notifications"

export const Digestate = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { year } = useParams<{ year: string }>()
  const notify = useNotify()
  const years = useYears("biomethane/digestate", getYears)
  const { result: digestate, loading } = useQuery(getDigestate, {
    key: "digestate",
    params: [entity.id, years.selected],
  })
  const validateDigestateMutation = useMutation(
    () => validateDigestate(entity.id),
    {
      invalidates: ["digestate"],
      onSuccess: () => {
        notify(t("Les informations ont bien été validées."), {
          variant: "success",
        })
      },
    }
  )

  const { result: productionUnit } = useProductionUnit()
  const { result: contract } = useGetContractInfos()
  usePrivateNavigation(t("Digestat"))

  if (loading) return <LoaderOverlay />

  if (!loading && !productionUnit?.id) {
    return <SettingsNotFilled />
  }

  return (
    <DigestateProvider year={years.selected}>
      <BiomethanePageHeader
        selectedYear={parseInt(year!)}
        yearsOptions={years.options}
        status={digestate?.data?.status}
        onChangeYear={years.setYear}
        onConfirm={validateDigestateMutation.execute}
      >
        {productionUnit && (
          <Production
            digestate={digestate?.data}
            productionUnit={productionUnit}
          />
        )}

        {productionUnit?.digestate_valorization_methods?.includes(
          DigestateValorizationMethods.SPREADING
        ) && (
          <>
            <SpreadingDistance digestate={digestate?.data} />
            <Spreading digestate={digestate?.data} />
          </>
        )}

        {productionUnit?.digestate_valorization_methods?.includes(
          DigestateValorizationMethods.COMPOSTING
        ) && <Composting digestate={digestate?.data} />}

        {productionUnit?.digestate_valorization_methods?.includes(
          DigestateValorizationMethods.INCINERATION_LANDFILLING
        ) && (
          <IncinerationLandfill
            digestate={digestate?.data}
            contract={contract}
          />
        )}

        {productionUnit?.spreading_management_methods?.includes(
          SpreadingManagementMethods.SALE
        ) && <Sale digestate={digestate?.data} />}
      </BiomethanePageHeader>
    </DigestateProvider>
  )
}
