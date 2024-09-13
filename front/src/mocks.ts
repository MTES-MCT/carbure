import { setupWorker } from "msw/browser"

import * as elecAdminAuditMocks from "elec-audit-admin/__test__/api"
import * as elecAuditMocks from "elec-auditor/__test__/api"
import * as elecMocks from "elec/__test__/api"
import { okInviteUser } from "settings/__test__/api"
import * as elecChargePointsMocks from "elec-charge-points/__test__/api"
import * as elecChargePointsListPageMocks from "elec-charge-points/pages/list/__test__/api"
export const worker = setupWorker(
  ...Object.values(elecAdminAuditMocks),
  ...Object.values(elecMocks),
  ...Object.values(elecAuditMocks),
  okInviteUser,
  ...Object.values(elecChargePointsMocks),
  ...Object.values(elecChargePointsListPageMocks)
)
