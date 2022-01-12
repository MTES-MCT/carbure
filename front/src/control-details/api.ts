import api, { Api } from "common-v2/services/api";
import { LotDetails } from "lot-details/types";

export function getLotDetails(entity_id: number, lot_id: number) {
  return api.get<Api<LotDetails>>("/admin/lots/details", {
    params: { entity_id, lot_id },
  });
}
