import { useAnnualDeclarationTiruertYears } from "accounting/hooks/use-annual-declaration-tiruert-years"
import { Select } from "common/components/selects2"

type ObjectivesYearSelectProps = {
  urlRoot: string
}

export const ObjectivesYearSelect = ({
  urlRoot,
}: ObjectivesYearSelectProps) => {
  const years = useAnnualDeclarationTiruertYears(urlRoot)

  return (
    <Select
      options={years.options}
      value={years.selected}
      onChange={years.setYear}
    />
  )
}
