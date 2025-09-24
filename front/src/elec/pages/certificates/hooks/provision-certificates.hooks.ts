import { useQuery } from "common/hooks/async"
import { getProvisionCertificateBalance } from "../api"
import useEntity from "common/hooks/entity"
import { formatUnit } from "common/utils/formatters"
import { ExtendedUnit } from "common/types"

export const useProvisionCertificatesBalance = () => {
  const entity = useEntity()

  const balanceResponse = useQuery(getProvisionCertificateBalance, {
    key: "elec-provision-certificate-balance",
    params: [entity.id],
  })

  const balance = balanceResponse.result?.data?.balance ?? 0

  return {
    balance,
    formattedBalance: formatUnit(balance, ExtendedUnit.MWh),
  }
}
