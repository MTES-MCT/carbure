import { useQuery } from "common/hooks/async"
import { getBiomethaneProducers } from "../api"
import useEntity from "common/hooks/entity"
import { BiomethaneProducer } from "../types"

export const useBiomethaneProducers = ({
  onSuccess,
}: {
  onSuccess?: (producers: BiomethaneProducer[]) => void
} = {}) => {
  const entity = useEntity()
  const { result: producers, loading } = useQuery(getBiomethaneProducers, {
    key: "biomethane-producers",
    params: [entity.id],
    onSuccess,
  })

  const isEntityMatchWithProducers = (selectedEntityId: string | number) =>
    producers?.some((producer) => producer.id === Number(selectedEntityId))

  return {
    producers,
    loading,
    isEntityMatchWithProducers,
  }
}
