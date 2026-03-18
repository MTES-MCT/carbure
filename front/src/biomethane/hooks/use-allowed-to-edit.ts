import useEntity from "common/hooks/entity"

/**
 * This hook is used to check if the entity can edit the contract/production/injection page
 * Only biomethane producers with write rights can edit these pages
 */
export const useAllowedToEdit = () => {
  const entity = useEntity()
  return entity.canWrite() && entity.isBiomethaneProducer
}
