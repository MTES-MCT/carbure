import { EntitySelection } from "../helpers/use-entity"

import * as api from "../../services/lots"
import useAPI from "../helpers/use-api"

export interface LotUploader {
  loading: boolean
  data: any
  error: string | null
  uploadFile: (f: File) => void
  uploadMassBalanceFile: (f: File) => void
  downloadTemplateSimple: () => void
  downloadTemplateAdvanced: () => void
  downloadTemplateMassBalance: () => void
  downloadTemplateOperator: () => void
}

export default function useUploadLotFile(
  entity: EntitySelection,
  refresh: () => void
): LotUploader {
  const [request, resolveUpload] = useAPI(api.uploadLotFile)
  const [requestMB, resolveUploadMassBalance] = useAPI(
    api.uploadMassBalanceFile
  )

  async function uploadFile(file: File) {
    if (entity !== null) {
      resolveUpload(entity.id, file).then(refresh)
    }
  }

  async function uploadMassBalanceFile(file: File) {
    if (entity !== null) {
      resolveUploadMassBalance(entity.id, file).then(refresh)
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

  function downloadTemplateMassBalance() {
    if (entity !== null) {
      api.downloadTemplateMassBalance(entity.id)
    }
  }

  function downloadTemplateOperator() {
    if (entity !== null) {
      api.downloadTemplateOperator(entity.id)
    }
  }

  return {
    ...request,
    uploadFile,
    uploadMassBalanceFile,
    downloadTemplateSimple,
    downloadTemplateAdvanced,
    downloadTemplateMassBalance,
    downloadTemplateOperator,
  }
}
