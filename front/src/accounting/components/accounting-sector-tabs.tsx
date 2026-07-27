import { Tabs } from "common/components/tabs2"
import { compact } from "common/utils/collection"
import { useTranslation } from "react-i18next"
import { SectorTabs } from "accounting/types"
import { useAccountingPermissions } from "accounting/hooks/use-accounting-permissions"

type AccountingSectorTabsProps = {
  pathPrefix?: string
}

export const AccountingSectorTabs = ({
  pathPrefix,
}: AccountingSectorTabsProps) => {
  const { t } = useTranslation()
  const { canAccessElecSector } = useAccountingPermissions()

  const getPath = (sectorTab: SectorTabs) =>
    pathPrefix ? `${pathPrefix}/${sectorTab}` : sectorTab

  return (
    <Tabs
      tabs={compact([
        {
          key: SectorTabs.BIOFUELS,
          label: t("Biocarburants"),
          path: getPath(SectorTabs.BIOFUELS),
          icon: "fr-icon-gas-station-fill",
        },
        canAccessElecSector && {
          key: SectorTabs.ELEC,
          label: t("Électricité"),
          path: getPath(SectorTabs.ELEC),
          icon: "fr-icon-charging-pile-2-fill",
        },
      ])}
    />
  )
}
