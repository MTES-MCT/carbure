import * as elecAdminAuditMocks from "elec-audit-admin/__test__/api"
import * as elecMocks from "elec/__test__/api"


export default [
  ...Object.values(elecAdminAuditMocks),
  ...Object.values(elecMocks)
]
