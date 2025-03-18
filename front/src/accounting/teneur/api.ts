type Objectives = {
  global: {
    objective: number // tCO2
    teneur_declared: number // TC02
    quantity_available: number // tC02
    teneur_declared_month: number // TC02
  }
}
export const getObjectives = async (
  entity_id: number,
  year: number
): Promise<Objectives> => {
  return new Promise((resolve) => {
    resolve({
      global: {
        objective: 16, // tCO2
        teneur_declared: 1, // TC02
        teneur_declared_month: 14, // TC02
        quantity_available: 100, // tC02
      },
    })
  })
}
