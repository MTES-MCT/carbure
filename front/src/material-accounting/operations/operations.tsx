import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"

export const Operations = () => {
  return (
    <>
      <FilterMultiSelect2
        filterLabels={{ filtre1: "Filtre 1", filtre2: "Filtre 2" }}
        selected={{}}
        onSelect={() => {}}
        getFilterOptions={() => Promise.resolve([])}
      />
    </>
  )
}
