import { Biofuel } from "common/types"

const SAF_BIOFUEL_TYPES = ["HVOC", "HOC", "HCC"]

export function isSAF(biofuel?: Biofuel) {
  if (!biofuel) return false
  else return SAF_BIOFUEL_TYPES.includes(biofuel.code)
}
