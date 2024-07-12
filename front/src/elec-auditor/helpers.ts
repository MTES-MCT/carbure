


export const getApplicationAuditLimitDate = (audit_order_date: string) => {
  let limitDate = new Date(audit_order_date)
  limitDate.setDate(limitDate.getDate() + 21)
  return limitDate
}


