import { Select } from "common/components/selects2"
import { useSelectableDeclarationYears } from "biomethane/hooks/use-selectable-declaration-years"

export const SelectYears = ({ urlRoot }: { urlRoot: string }) => {
  const years = useSelectableDeclarationYears(urlRoot)
  return (
    <Select
      options={years.options}
      value={years.selected}
      onChange={years.setYear}
    />
  )
}
