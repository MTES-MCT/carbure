import { Dialog } from "common/components/dialog2"
import { getQualichargeDataGroupedByOperatingUnit } from "../api"
import { useQuery } from "common/hooks/async"
import {
  ElecDataQualichargeGroupedByOperatingUnit,
  QualichargeQuery,
} from "../types"
import { LoaderOverlay } from "common/components/scaffold"
import { Cell, Column, Table } from "common/components/table2"
import useEntity from "common/hooks/entity"
import { compact } from "common/utils/collection"
import { ExternalAdminPages } from "common/types"
import { useTranslation } from "react-i18next"
import { formatDate, formatNumber } from "common/utils/formatters"
import { RecapQuantity } from "common/molecules/recap-quantity"
import { Text } from "common/components/text"

export type ValidateAllDataDialogProps = {
  onClose: () => void
  query: QualichargeQuery
}

export const ValidateAllDataDialog = ({
  onClose,
  query,
}: ValidateAllDataDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { result, loading } = useQuery(
    getQualichargeDataGroupedByOperatingUnit,
    {
      key: "qualicharge-data-grouped-by-operating-unit",
      params: [query],
    }
  )
  if (!result && loading) {
    return <LoaderOverlay />
  }

  const columns: Column<ElecDataQualichargeGroupedByOperatingUnit>[] = compact([
    (entity.isAdmin || entity.hasAdminRight(ExternalAdminPages.ELEC)) && {
      header: t("Aménageur"),
      cell: (data) => <Cell text={data.cpo.name} />,
    },
    {
      header: t("Unité d'exploitation"),
      cell: (data) => <Cell text={data.operating_unit} />,
    },
    {
      header: t("Début de la mesure"),
      cell: (data) => <Cell text={formatDate(data.date_from)} />,
    },
    {
      header: t("Fin de la mesure"),
      cell: (data) => <Cell text={formatDate(data.date_to)} />,
    },
    {
      header: t("Energie (MWh)"),
      cell: (data) => (
        <Cell text={formatNumber(data.energy_amount, { fractionDigits: 2 })} />
      ),
    },
  ])

  return (
    <Dialog
      header={<Dialog.Title>Valider toutes les données</Dialog.Title>}
      onClose={onClose}
      size="large"
    >
      <Text>
        Cette vue récapitule les données Qualicharge à valider groupées par
        unité d'exploitation et debut/fin de mesure. Vérifiez les données et
        validez les volumes.
      </Text>
      <RecapQuantity
        text={t("{{count}} volumes pour un total de {{total}} MWh", {
          count: result?.data?.count,
          total: formatNumber(result?.data?.total_quantity ?? 0, {
            fractionDigits: 0,
          }),
        })}
      />
      <Table
        columns={columns}
        rows={result?.data?.results ?? []}
        loading={loading}
      />
    </Dialog>
  )
}
