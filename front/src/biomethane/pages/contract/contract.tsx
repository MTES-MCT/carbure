import { ContractAmendments } from "./components/contract-amendments/contract-amendments"
import { ContractFiles } from "./components/contract-files"
import { ContractInfos } from "./components/contract-infos"
import { useGetContractInfos } from "./contract.hooks"
import { ErrorTrackedAmendmentTypes } from "./components/tracked-amendment-types"

export const BiomethaneContractPage = () => {
  const { result: contractInfos, loading } = useGetContractInfos()

  return (
    <>
      {contractInfos && contractInfos.tracked_amendment_types.length > 0 && (
        <ErrorTrackedAmendmentTypes
          trackedAmendmentTypes={contractInfos.tracked_amendment_types}
        />
      )}
      {/* 
        Render ContractInfos component in two cases:
          - When contract data is available (contractInfos exists)
          - When no data is available AND loading is finished (!loading)
      */}
      {(contractInfos || (!contractInfos && !loading)) && (
        <ContractInfos contract={contractInfos} />
      )}
      <ContractFiles contract={contractInfos} />
      <ContractAmendments contract={contractInfos} />
    </>
  )
}
