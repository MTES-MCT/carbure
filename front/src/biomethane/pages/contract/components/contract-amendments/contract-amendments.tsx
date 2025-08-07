import { useTranslation } from "react-i18next"
import { Column, Table, Cell } from "common/components/table2"
import { Button } from "common/components/button2"
import { Notice } from "common/components/notice"
import { EditableCard } from "common/molecules/editable-card"
import {
  BiomethaneEntityConfigAmendment,
  BiomethaneEntityConfigContract,
} from "biomethane/types"
import { usePortal } from "common/components/portal"
import { AddAmendment } from "./add-amendment"

export const ContractAmendments = ({
  contract,
}: {
  contract?: BiomethaneEntityConfigContract
}) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const amendments = contract?.amendments ?? []

  const columns: Column<BiomethaneEntityConfigAmendment>[] = [
    {
      header: t("N° avenant"),
      cell: (amendment) => <Cell text={amendment.id.toString()} />,
    },
    {
      header: t("Date de signature"),
      cell: (amendment) => <Cell text={amendment.signature_date} />,
    },
    {
      header: t("Date de prise d'effet"),
      cell: (amendment) => <Cell text={amendment.effective_date} />,
    },
    {
      header: t("Télécharger"),
      cell: (amendment) => (
        <Button
          priority="tertiary no outline"
          iconId="ri-download-line"
          linkProps={{
            href: amendment.amendment_file,
            target: "_blank",
          }}
          size="small"
          title={t("Télécharger")}
        />
      ),
    },
  ]

  const openAddAmendmentDialog = () => {
    portal((close) => <AddAmendment onClose={close} />)
  }

  return (
    <EditableCard
      title={t("Avenants au contrat d'achat")}
      headerActions={
        <Button
          iconId="ri-add-line"
          disabled={
            !contract || (contract && !contract.general_conditions_file)
          }
          onClick={openAddAmendmentDialog}
        >
          {t("Charger un avenant")}
        </Button>
      }
    >
      {amendments.length === 0 ? (
        <Notice variant="warning" icon="ri-error-warning-line">
          {t("Aucun avenant associé au contrat.")}
        </Notice>
      ) : (
        <Table rows={amendments} columns={columns} />
      )}
    </EditableCard>
  )
}
