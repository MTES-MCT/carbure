import { setupWorker } from "msw/browser"

import * as elecAuditMocks from "elec-auditor/__test__/api"
import * as elecMocks from "elec-charge-points/__test__/api"
import * as elecChargePointsMocks from "elec-charge-points/__test__/api"
import * as elecChargePointsListPageMocks from "elec-charge-points/pages/list/__test__/api"

export const worker = setupWorker(
  ...Object.values(elecMocks),
  ...Object.values(elecAuditMocks),
  ...Object.values(elecChargePointsMocks),
  ...Object.values(elecChargePointsListPageMocks)
)
