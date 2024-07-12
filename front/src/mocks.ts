import { setupWorker } from "msw"

import * as elecAdminAuditMocks from "elec-audit-admin/__test__/api"
import * as elecAuditMocks from "elec-auditor/__test__/api"
import * as elecMocks from "elec/__test__/api"

export const worker = setupWorker(
  ...Object.values(elecAdminAuditMocks),
  ...Object.values(elecMocks),
  ...Object.values(elecAuditMocks),
)
