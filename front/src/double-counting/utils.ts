export const isAgreementExpired = (expirationDate: string) =>
  new Date(expirationDate) < new Date()
