import Alert from "common/components/alert"
import Button from "common/components/button"
import { Bolt } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { formatNumber } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import EnergyTransferDialog from "./transfer-dialog"

export interface EnergyTransferSummaryProps {
    remainingVolume: number
}

export const EnergyTransferSummary = ({
    remainingVolume,
}: EnergyTransferSummaryProps) => {
    const { t } = useTranslation()
    const portal = usePortal()

    const notify = useNotify()

    const onEnergyTransferred = (volume: number, clientName: string) => {
        notify(t("{{volume}} MWh ont bien été transférés au redevable {{clientName}}", { volume: formatNumber(volume, 3), clientName }), { variant: "success" })
    }

    const showEnergyTransferModal = () => {
        portal((close) => (
            <EnergyTransferDialog onClose={close} remainingEnergy={remainingVolume} onEnergyTransferred={onEnergyTransferred} />
        ))
    }

    return (
        <Alert icon={Bolt} variant="info" style={{ display: "flex", alignItems: "center" }}>
            <p>
                {t(
                    "{{remainingVolume}} MWh restants",
                    {
                        remainingVolume: formatNumber(remainingVolume, 3),
                    }
                )}
            </p>

            <Button
                asideX
                variant="primary"
                label={t("Réaliser une cession d'énergie")}
                action={showEnergyTransferModal}
            />
        </Alert>
    )
}
