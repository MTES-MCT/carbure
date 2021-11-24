import { EntityManager } from "carbure/hooks/entity"

import * as api from "../api"
import useAPI from "common/hooks/use-api"
import { Option, SelectValue } from "common/components/select"
import { useEffect } from "react"
import { ProductionCertificate } from "common/types"
import { reloadUserSettings } from "carbure/hooks/user"

export function toggleMAC(toggle: boolean, entityID: number) {
  return toggle ? api.enableMAC(entityID) : api.disableMAC(entityID)
}

export function toggleTrading(toggle: boolean, entityID: number) {
  return toggle ? api.enableTrading(entityID) : api.disableTrading(entityID)
}

export interface CompanySettingsHook {
  isLoading: boolean
  hasMAC: boolean
  hasTrading: boolean
  certificates: Option[]
  defaultCertificate: ProductionCertificate | null
  onChangeMAC: (checked: boolean) => void
  onChangeTrading: (checked: boolean) => void
  onChangeDefaultCertificate: (certificate: SelectValue) => void
  refresh: () => void
}

export default function useCompany(entity: EntityManager): CompanySettingsHook {
  const hasMAC: boolean = entity.has_mac ?? false
  const hasTrading: boolean = entity.has_trading ?? false

  const [requestMAC, resolveToggleMAC] = useAPI(toggleMAC)
  const [requestTrading, resolveToggleTrading] = useAPI(toggleTrading)

  const [requestDefaultCert, setDefaultCertificate] = useAPI(api.setDefaultCertificate) // prettier-ignore
  const [certificates, findCertificates] = useAPI(api.findCertificates)

  const entityID = entity.id ?? -1

  useEffect(() => {
    if (entityID >= 0) {
      findCertificates("", entityID)
    }
  }, [findCertificates, entityID])

  const isLoading =
    certificates.loading ||
    requestMAC.loading ||
    requestTrading.loading ||
    requestDefaultCert.loading

  const defaultCertificate =
    certificates.data?.find(
      (c) => c.certificate_id === entity.default_certificate
    ) ?? null

  const certificateOptions = certificates.data?.map((c) => ({
    value: c.certificate_id,
    label: `${c.certificate_id} - ${c.holder}`,
  }))

  function refresh() {
    if (entity) {
      findCertificates("", entityID)
    }
  }

  function onChangeMAC(checked: boolean): void {
    if (entity !== null) {
      resolveToggleMAC(checked, entityID)
      reloadUserSettings()
    }
  }

  function onChangeTrading(checked: boolean): void {
    if (entity !== null) {
      resolveToggleTrading(checked, entityID)
      reloadUserSettings()
    }
  }

  async function onChangeDefaultCertificate(certificateID: SelectValue) {
    const certificate = certificates.data?.find(
      (c) => c.certificate_id === certificateID
    )

    if (entity && certificate) {
      await setDefaultCertificate(
        entityID,
        certificate.certificate_id,
        certificate.type.toUpperCase()
      )

      reloadUserSettings()
    }
  }

  return {
    isLoading,
    hasMAC,
    hasTrading,
    certificates: certificateOptions ?? [],
    defaultCertificate,
    onChangeMAC,
    onChangeTrading,
    onChangeDefaultCertificate,
    refresh,
  }
}
