import Dialog from "common/components/dialog2/dialog"
import { Notice } from "common/components/notice"
import Portal from "common/components/portal"
import { Grid, Main } from "common/components/scaffold"
import { formatNumber } from "common/utils/formatters"
import { Balance } from "accounting/balances/types"
import { OperationText } from "accounting/components/operation-text"
import { Trans, useTranslation } from "react-i18next"
import { formatSector } from "accounting/utils/formatters"

interface CessionDialogProps {
  onClose: () => void
  balance: Balance
}

export const CessionDialog = ({ onClose, balance }: CessionDialogProps) => {
  const { t } = useTranslation()

  return (
    <Portal>
      <Dialog
        fullWidth
        onClose={onClose}
        header={
          <Dialog.Title>
            <Trans>Réaliser une cession</Trans>
          </Dialog.Title>
        }
      >
        <Main>
          <Grid>
            <OperationText
              title={t("Filière")}
              description={formatSector(balance.sector)}
            />
            <OperationText
              title={t("Catégorie")}
              description={balance.customs_category ?? ""}
            />
            <OperationText
              title={t("Biocarburant")}
              description={balance.biofuel ?? ""}
            />
          </Grid>
          <Notice variant="info" noColor>
            <Trans>Solde disponible</Trans> {balance.biofuel}
            {" : "}
            <b>{formatNumber(Number(balance.available_balance))}l</b>
          </Notice>
        </Main>
      </Dialog>
    </Portal>
  )
}
