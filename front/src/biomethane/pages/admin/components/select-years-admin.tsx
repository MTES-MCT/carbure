import { Select } from "common/components/selects2"
import { useAnnualDeclarationYearsAdmin } from "../hooks/use-annual-declaration-years-admin"

// Use a separate component to set a key to the select to force a re-render when the selected entity changes
export const SelectYearsAdmin = ({ urlRoot }: { urlRoot: string }) => {
  const years = useAnnualDeclarationYearsAdmin(urlRoot)
  return (
    <Select
      options={years.options}
      value={years.selected}
      onChange={years.setYear}
    />
  )
}
