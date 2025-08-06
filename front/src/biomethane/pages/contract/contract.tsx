import { ContractInfos } from "./components/contract-infos"
import { useGetContractInfos } from "biomethane/hooks/contract.hooks"

export const BiomethaneContractPage = () => {
  const { result: contractInfos } = useGetContractInfos()

  const contract = contractInfos?.results[0]

  return (
    <>
      <ContractInfos contract={contract} />
    </>
  )
}
