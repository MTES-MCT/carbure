import Alert from "common/components/alert"
import Button from "common/components/button"
import { Bolt } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { formatNumber } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import EnergyTransferDialog from "./transfer-dialog"

export interface EnergyTransferSummaryProps {
  remainingEnergy: number
  readonly: boolean
}

export const EnergyTransferSummary = ({
  remainingEnergy,
  readonly,
}: EnergyTransferSummaryProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  const notify = useNotify()

  const onEnergyTransferred = (energy: number, clientName: string) => {
    notify(
      t("{{energy}} MWh ont bien été transférés au redevable {{clientName}}", {
        energy: formatNumber(energy, 3),
        clientName,
      }),
      { variant: "success" }
    )
  }

  const showEnergyTransferModal = () => {
    portal((close) => (
      <EnergyTransferDialog
        onClose={close}
        remainingEnergy={remainingEnergy}
        onEnergyTransferred={onEnergyTransferred}
      />
    ))
  }

  return (
    <Alert icon={Bolt} variant="info">
      <p>
        {t("{{remainingEnergy}} MWh restants", {
          remainingEnergy: formatNumber(remainingEnergy, 3),
        })}
      </p>

      {!readonly && (
        <Button
          asideX
          variant="primary"
          label={t("Réaliser une cession d'énergie")}
          action={showEnergyTransferModal}
        />
      )}
    </Alert>
  )
}
