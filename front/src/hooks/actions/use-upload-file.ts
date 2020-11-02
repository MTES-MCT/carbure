import { EntitySelection } from "../helpers/use-entity"

import * as api from "../../services/lots"
import useAPI from "../helpers/use-api"

export interface LotUploader {
  loading: boolean
  data: any
  error: string | null
  uploadFile: (f: File) => void
  downloadTemplateSimple: () => void
  downloadTemplateAdvanced: () => void
}

export default function useUploadLotFile(
  entity: EntitySelection,
  refresh: () => void
): LotUploader {
  const [request, resolveUpload] = useAPI(api.uploadLotFile)

  async function uploadFile(file: File) {
    if (entity !== null) {
      resolveUpload(entity.id, file).then(refresh)
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

  return {
    ...request,
    uploadFile,
    downloadTemplateSimple,
    downloadTemplateAdvanced,
  }
}
