import { EntitySelection } from "carbure/hooks/use-entity"

import * as api from "transactions/api"
import useAPI from "../../../common/hooks/use-api"
import { useNotificationContext } from "../../../common/components/notifications"

export interface LotUploader {
  loading: boolean
  data: any
  error: string | null
  uploadFile: (f: File) => void
  uploadMassBalanceFile: (f: File) => void
  uploadOperatorFile: (f: File) => void
  downloadTemplateSimple: () => void
  downloadTemplateAdvanced: () => void
  downloadTemplateMassBalanceCarbureID: () => void
  downloadTemplateMassBalanceBCGHG: () => void
  downloadTemplateOperator: () => void
  downloadTemplateTrader: () => void
}

export default function useUploadLotFile(
  entity: EntitySelection,
  refresh: () => void
): LotUploader {
  const notifications = useNotificationContext()

  const [request, resolveUpload] = useAPI(api.uploadLotFile)
  const [, resolveUploadMassBalance] = useAPI(api.uploadMassBalanceFile)
  const [, resolveUploadOperator] = useAPI(api.uploadOperatorLotFile)

  async function notifyImport(promise: Promise<any>) {
    const startNotif = notifications.push({
      text: "L'importation a débuté, veuillez patienter.",
    })

    const res: any = await promise

    if (res) {
      const level =
        res.loaded === 0
          ? "error"
          : res.loaded < res.total
          ? "warning"
          : "success"

      notifications.dispose(startNotif.key)

      notifications.push({
        level,
        text: `${res.loaded} lots sur ${res.total} ont été importées depuis le fichier.`,
      })

      refresh()
    } else {
      notifications.dispose(startNotif.key)

      notifications.push({
        level: "error",
        text: "Le fichier n'a pas pu être importé.",
      })
    }
  }

  function uploadFile(file: File) {
    if (entity !== null) {
      notifyImport(resolveUpload(entity.id, file))
    }
  }

  async function uploadMassBalanceFile(file: File) {
    if (entity !== null) {
      notifyImport(resolveUploadMassBalance(entity.id, file))
    }
  }

  async function uploadOperatorFile(file: File) {
    if (entity !== null) {
      notifyImport(resolveUploadOperator(entity.id, file))
    }
  }

  function downloadTemplateSimple() {
    if (entity !== null) {
      api.downloadTemplateSimple(entity.id)
    }
  }

  function downloadTemplateAdvanced() {
    if (entity !== null) {
      api.downloadTemplateAdvanced(entity.id)
    }
  }

  function downloadTemplateMassBalanceCarbureID() {
    if (entity !== null) {
      api.downloadTemplateMassBalanceCarbureID(entity.id)
    }
  }

  function downloadTemplateMassBalanceBCGHG() {
    if (entity !== null) {
      api.downloadTemplateMassBalanceBCGHG(entity.id)
    }
  }

  function downloadTemplateOperator() {
    if (entity !== null) {
      api.downloadTemplateOperator(entity.id)
    }
  }

  function downloadTemplateTrader() {
    if (entity !== null) {
      api.downloadTemplateTrader(entity.id)
    }
  }

  return {
    ...request,
    uploadFile,
    uploadMassBalanceFile,
    uploadOperatorFile,
    downloadTemplateSimple,
    downloadTemplateAdvanced,
    downloadTemplateMassBalanceCarbureID,
    downloadTemplateMassBalanceBCGHG,
    downloadTemplateOperator,
    downloadTemplateTrader,
  }
}
