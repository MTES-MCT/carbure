import { EntityManager } from "carbure/hooks/entity"

import * as api from "../api"
import * as api2 from "../api-v2"
import useAPI from "common/hooks/use-api"
import { useQuery, useMutation } from "common-v2/hooks/async"
import { Option, SelectValue } from "common/components/select"
import { EntityCertificate } from "common/types"
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
  defaultCertificate: EntityCertificate | null
  onChangeMAC: (checked: boolean) => void
  onChangeTrading: (checked: boolean) => void
  onChangeDefaultCertificate: (certificate: SelectValue) => void
}

export default function useCompany(entity: EntityManager): CompanySettingsHook {
  const hasMAC: boolean = entity.has_mac ?? false
  const hasTrading: boolean = entity.has_trading ?? false

  const [requestMAC, resolveToggleMAC] = useAPI(toggleMAC)
  const [requestTrading, resolveToggleTrading] = useAPI(toggleTrading)

  const certificates = useQuery(api2.getMyCertificates, {
    key: "entity-certificates",
    params: [entity!.id],
  })

  const setDefaultCertificate = useMutation(api2.setDefaultCertificate, {
    invalidates: ["user-settings"],
  })

  const entityID = entity.id ?? -1

  const isLoading =
    certificates.loading ||
    requestMAC.loading ||
    requestTrading.loading ||
    setDefaultCertificate.loading

  const entityCertificates = certificates.result?.data?.data ?? []

  const defaultCertificate =
    entityCertificates.find(
      (c) => c.certificate.certificate_id === entity.default_certificate
    ) ?? null

  const certificateOptions = entityCertificates.map((c) => ({
    value: c.certificate.certificate_id,
    label: `${c.certificate.certificate_id} - ${c.certificate.certificate_holder}`,
  }))

  async function onChangeMAC(checked: boolean) {
    if (entity !== null) {
      await resolveToggleMAC(checked, entityID)
      reloadUserSettings()
    }
  }

  async function onChangeTrading(checked: boolean) {
    if (entity !== null) {
      await resolveToggleTrading(checked, entityID)
      reloadUserSettings()
    }
  }

  async function onChangeDefaultCertificate(certificateID: SelectValue) {
    const certificate = entityCertificates.find(
      (c) => c.certificate.certificate_id === certificateID
    )

    if (entity && certificate) {
      setDefaultCertificate.execute(
        entityID,
        certificate.certificate.certificate_id
      )
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
  }
}
