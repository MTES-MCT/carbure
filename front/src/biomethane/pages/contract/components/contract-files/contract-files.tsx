import { useTranslation } from "react-i18next"
import { Column, Table, Cell } from "common/components/table2"
import { Button } from "common/components/button2"
import { Notice } from "common/components/notice"
import { EditableCard } from "common/molecules/editable-card"
import { BiomethaneEntityConfigContract } from "biomethane/types"
import { DateInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { usePortal } from "common/components/portal"
import { AddContract } from "./add-contract"

type ContractFile = {
  name: string
  url?: string | null
}

export const ContractFiles = ({
  contract,
}: {
  contract?: BiomethaneEntityConfigContract
}) => {
  const { t } = useTranslation()
  const portal = usePortal()

  const files: ContractFile[] = [
    {
      name: t("Conditions générales"),
      url: contract?.general_conditions_file,
    },
    {
      name: t("Conditions spécifiques"),
      url: contract?.specific_conditions_file,
    },
  ].filter((file) => file.url !== null)

  const columns: Column<ContractFile>[] = [
    {
      header: t("Nom"),
      cell: (file) => <Cell text={file.name} />,
    },
    {
      header: t("Télécharger"),
      cell: (file) => (
        <Button
          priority="tertiary no outline"
          iconId="ri-download-line"
          linkProps={{
            href: file.url ?? "",
            target: "_blank",
          }}
          size="small"
          title={t("Télécharger")}
        />
      ),
    },
  ]

  const openAddContractDialog = () => {
    portal((close) => <AddContract onClose={close} />)
  }

  return (
    <EditableCard
      title={t("Conditions générales et particulières")}
      headerActions={
        <Button
          iconId="ri-add-line"
          disabled={!contract || Boolean(contract.general_conditions_file)}
          onClick={openAddContractDialog}
        >
          {t("Charger un contrat")}
        </Button>
      }
    >
      {files.length === 0 ? (
        <Notice variant="warning" icon="ri-error-warning-line">
          {t("Aucun fichier associé au contrat.")}
        </Notice>
      ) : (
        <>
          <Grid cols={2} gap="lg">
            <DateInput
              readOnly
              value={contract?.signature_date ?? ""}
              label={t("Date de signature")}
            />
            <DateInput
              readOnly
              value={contract?.effective_date ?? ""}
              label={t("Date de prise d'effet")}
            />
          </Grid>

          <Table rows={files} columns={columns} />
        </>
      )}
    </EditableCard>
  )
}
