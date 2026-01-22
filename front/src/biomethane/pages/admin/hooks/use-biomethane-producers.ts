import { useQuery } from "common/hooks/async"
import { getBiomethaneProducers } from "../api"
import useEntity from "common/hooks/entity"

export const useBiomethaneProducers = () => {
  const entity = useEntity()
  const { result: producers, loading } = useQuery(getBiomethaneProducers, {
    key: "biomethane-producers",
    params: [entity.id],
  })

  const isEntityMatchWithProducers = (selectedEntityId: string | number) =>
    producers?.some((producer) => producer.id === Number(selectedEntityId))

  return { producers, loading, isEntityMatchWithProducers }
}
