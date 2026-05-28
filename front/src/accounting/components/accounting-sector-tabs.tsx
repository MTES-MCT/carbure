import { Tabs } from "common/components/tabs2"
import { compact } from "common/utils/collection"
import { useTranslation } from "react-i18next"
import { SectorTabs } from "accounting/types"
import useEntity from "common/hooks/entity"

type AccountingSectorTabsProps = {
  pathPrefix?: string
}

export const AccountingSectorTabs = ({
  pathPrefix,
}: AccountingSectorTabsProps) => {
  const { t } = useTranslation()
  const { has_elec, isOperator, isAdmin, hasAdminRight } = useEntity()

  const getPath = (sectorTab: SectorTabs) =>
    pathPrefix ? `${pathPrefix}/${sectorTab}` : sectorTab

  const showElecTab =
    (isOperator && has_elec) || isAdmin || hasAdminRight("ELEC")

  return (
    <Tabs
      tabs={compact([
        {
          key: SectorTabs.BIOFUELS,
          label: t("Biocarburants"),
          path: getPath(SectorTabs.BIOFUELS),
          icon: "fr-icon-gas-station-fill",
        },
        showElecTab && {
          key: SectorTabs.ELEC,
          label: t("Électricité"),
          path: getPath(SectorTabs.ELEC),
          icon: "fr-icon-charging-pile-2-fill",
        },
      ])}
    />
  )
}
