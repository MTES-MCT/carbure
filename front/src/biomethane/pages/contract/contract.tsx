import { ContractInfos } from "./components/contract-infos"
import { useGetContractInfos } from "biomethane/hooks/contract.hooks"

export const BiomethaneContractPage = () => {
  const { result: contractInfos, loading } = useGetContractInfos()

  return (
    <>
      {/* 
        Render ContractInfos component in two cases:
          - When contract data is available (contractInfos exists)
          - When no data is available AND loading is finished (!loading)
      */}
      {(contractInfos || (!contractInfos && !loading)) && (
        <ContractInfos contract={contractInfos} />
      )}
    </>
  )
}
