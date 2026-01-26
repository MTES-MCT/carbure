import { ContractAmendments } from "./components/contract-amendments/contract-amendments"
import { ContractFiles } from "./components/contract-files"
import { ContractInfos } from "./components/contract-infos"
import { useGetContractInfos } from "./contract.hooks"
import { ErrorTrackedAmendmentTypes } from "./components/tracked-amendment-types"
import { LoaderOverlay } from "common/components/scaffold"
import { AnnualDeclarationAlert } from "biomethane/components/annual-declaration-alert"
import { getContractWatchedFields } from "./api"
import { WatchedFieldsProvider } from "biomethane/providers/watched-fields"
import { ContractAidOrganism } from "./components/contract-aid-organism"
import { useSelectedEntity } from "common/providers/selected-entity-provider"

export const BiomethaneContractPage = () => {
  const { result: contractInfos, loading } = useGetContractInfos()
  const { hasSelectedEntity } = useSelectedEntity()

  if (loading) return <LoaderOverlay />

  return (
    <WatchedFieldsProvider
      apiFunction={getContractWatchedFields}
      queryKey="contract-watched-fields"
    >
      {!hasSelectedEntity && <AnnualDeclarationAlert />}
      {contractInfos && contractInfos.tracked_amendment_types.length > 0 && (
        <ErrorTrackedAmendmentTypes
          trackedAmendmentTypes={contractInfos.tracked_amendment_types}
        />
      )}
      {(contractInfos || (!contractInfos && !loading)) && (
        <ContractInfos contract={contractInfos} />
      )}
      <ContractFiles contract={contractInfos} />
      <ContractAmendments contract={contractInfos} />
      <ContractAidOrganism contract={contractInfos} />
    </WatchedFieldsProvider>
  )
}
