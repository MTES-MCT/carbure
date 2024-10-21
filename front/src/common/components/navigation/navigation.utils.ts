const mapToNeighbors = (map: Map<number, number[]>) =>
  [...map.entries()] // Récupérer les entrées (paires clé-valeur)
    .sort((a, b) => a[0] - b[0]) // Trier par les clés (a[0] et b[0] sont les clés)
    .flatMap(([, values]) => values) // Aplatir les valeurs dans un seul tableau

export const getNeighborsInfos = (
  mapIds: Map<number, number[]>,
  currentId: number,
  currentPage: number,
  pageCount: number
) => {
  const neighborsCurrentPage = mapIds.get(currentPage) ?? []
  const neighbors = mapToNeighbors(mapIds)

  const index = neighbors.indexOf(currentId)
  const indexCurrentPage = neighborsCurrentPage.indexOf(currentId)

  const isOut = index < 0
  const hasPrev = index > 0 || currentPage > 1
  const hasNext = index < neighbors.length - 1 || currentPage < pageCount
  const hasPrevCurrentPage = indexCurrentPage > 0
  const hasNextCurrentPage = indexCurrentPage < neighborsCurrentPage.length - 1

  return {
    index,
    isOut,
    hasPrev,
    hasNext,
    hasPrevCurrentPage,
    hasNextCurrentPage,
  }
}
