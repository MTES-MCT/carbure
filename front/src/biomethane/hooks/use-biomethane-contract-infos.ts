import { useGetContractInfos } from "biomethane/pages/contract/contract.hooks"

export const useBiomethaneContractInfos = () => {
  const { result: contractInfos, loading: loadingContract } =
    useGetContractInfos()

  return { contractInfos, loadingContract }
}
