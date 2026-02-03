import { Notice } from "common/components/notice"
import { useTranslation } from "react-i18next"
import { SendReadjustmentCertificatesDialog } from "./send-readjustment-certificates"
import { usePortal } from "common/components/portal"

type ReadjustmentNoticeProps = {
  balance: number
  formattedBalance: string
  readjustmentBalance: number
  formattedReadjustmentBalance: string
}

export const ReadjustmentNotice = ({
  balance,
  formattedBalance,
  readjustmentBalance,
  formattedReadjustmentBalance,
}: ReadjustmentNoticeProps) => {
  const { t } = useTranslation()

  const portal = usePortal()

  function showDialog() {
    portal((close) => (
      <SendReadjustmentCertificatesDialog
        onClose={close}
        balance={balance}
        formattedBalance={formattedBalance}
        readjustmentBalance={readjustmentBalance}
        formattedReadjustmentBalance={formattedReadjustmentBalance}
      />
    ))
  }

  return (
    <Notice
      variant="warning"
      title={t(
        "Un trop-perçu de {{balance}} a été détecté sur les certificats de fourniture",
        { balance: formattedReadjustmentBalance }
      )}
      linkText={t("Réajuster les certificats")}
      onAction={showDialog}
    />
  )
}
