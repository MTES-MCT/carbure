import useEntity from "carbure/hooks/entity"
import { useUser } from "carbure/hooks/user"
import { EntityPreview } from "carbure/types"
import * as norm from "carbure/utils/normalizers"
import Alert from "common/components/alert"
import Autocomplete from "common/components/autocomplete"
import Button, { MailTo } from "common/components/button"
import Dialog from "common/components/dialog"
import Form, { useForm } from "common/components/form"
import { AlertTriangle, ExternalLink, Message, Return, Send } from "common/components/icons"
import { NumberInput } from "common/components/input"
import { useMutation } from "common/hooks/async"
import { formatNumber } from "common/utils/formatters"
import * as api from "elec/api"
import { useTranslation } from "react-i18next"

export interface EnergyTransferDialogProps {
    onClose: () => void
    remainingEnergy: number
}
export const EnergyTransferDialog = ({
    onClose,
    remainingEnergy
}: EnergyTransferDialogProps) => {
    const { t } = useTranslation()
    const entity = useEntity()

    const { value, bind, setField, setFieldError } =
        useForm<TransferForm>(defaultTransfer)

    const transferEnergyRequest = useMutation(api.transferEnergy, {
        invalidates: [
            "provision-certificates",
        ],
        onSuccess: () => {
            alert('ok')
            // onTicketAssigned(value.volume!, value.client!.name)
            onClose()
        }
    })

    const transferEnergy = async () => {
        if (!value.client) {
            setFieldError("client", t("Entrez un redevable"))
            return
        }
        if (value.energy_mwh! < 1) {
            setFieldError("energy_mwh", t("Entrez une quantité d’énergie"))
            return
        }
        await transferEnergyRequest.execute(
            entity.id,
            value.energy_mwh!,
            value.client.id!
        )

    }

    const setMaximumEnergy = () => {
        setField("energy_mwh", remainingEnergy)
    }

    const findCPOClient = (query: string) => {
        return api.findClients(query)
    }

    return (

        <Dialog onClose={onClose}>
            <header>
                <h1>
                    {t("Cession d’un volume d’énergie")}
                </h1>
            </header>

            <main>
                <section>
                    <p>
                        {t(
                            "En cédant un volume d’énergie à un redevable, cela donnera lieu à l’édition d’un certificat de cession."
                        )}
                    </p>

                    <Form id="transfer-energy" onSubmit={transferEnergy}>
                        {/* Quantité MWh (35 000) */}
                        <EnergyInput
                            remainingEnergy={remainingEnergy}
                            setMaximumEnergy={setMaximumEnergy}
                            {...bind("energy_mwh")}
                        />
                        <p>{t("Les volumes d’énergie sont consommés de manière chronologique (les plus anciens sont vidés en premier).")}</p>

                        <Autocomplete
                            required
                            label={t("Redevable")}
                            getOptions={findCPOClient}
                            normalize={norm.normalizeEntityPreview}
                            {...bind("client")}
                        />

                    </Form>

                    <Alert variant="info" icon={AlertTriangle} style={{ display: "inline-block" }}>
                        {t('Si vous ne trouver pas le redevable concerné par la cession d’énergie dans notre base, veuillez')} {" "}
                        <AddElecOperatorMail clientName={value.client?.name} />
                    </Alert>
                    <Alert variant="info" icon={Message}>
                        {t('Une fois le certificat de cession édité et aloué à un redevable, celui-ci pourra l’accepter ou le refuser, en laissant un commentaire.')}
                    </Alert>
                </section>
            </main>

            <footer>
                <Button
                    loading={transferEnergyRequest.loading}
                    icon={Send}
                    label={t("Céder le certificat au redevable")}
                    variant="primary"
                    submit="transfer-energy"
                />

                <Button icon={Return} label={t("Retour")} action={onClose} />
            </footer>
        </Dialog>

    )
}

export default EnergyTransferDialog

const AddElecOperatorMail = ({ clientName = "[Nom du redevable]" }: { clientName?: string }) => {
    const { t } = useTranslation()
    const entity = useEntity()
    const user = useUser()

    return <MailTo user="valorisation-recharge" host="developpement-durable.gouv.fr"
        subject={t("[CarbuRe - Elec] Je ne trouve pas mon redevable")}
        body={t("Bonjour%2C%E2%80%A8%E2%80%A8%0D%0AEn%20tant%20que%20{{cpoName}}%2C%0D%0AJe%20souhaite%20que%20la%20soci%C3%A9t%C3%A9%20{{clientName}}%20soit%20ajout%C3%A9e%20%C3%A0%20la%20base%20de%20donn%C3%A9e%20CarbuRe%20afin%20de%20pouvoir%20lui%20c%C3%A9der%20un%20volume%20d%E2%80%99%C3%A9nergie.%0D%0ABien%20cordialement%0D%0A{{userEmail}}",
            // {cpoName: entity.name, clientName, userName: user.email, userFirstname: "Prénom", userEmail: user.email)}
            { cpoName: entity.name, clientName, userEmail: user.email })
        }

    >
        {t("contacter la DGEC")}
        <ExternalLink size={20} />
    </MailTo>

}

const defaultTransfer = {
    energy_mwh: 0 as number | undefined,
    client: undefined as EntityPreview | undefined,
}

export type TransferForm = typeof defaultTransfer



interface EnergyInputProps {
    remainingEnergy: number
    setMaximumEnergy: () => void
}

export const EnergyInput = ({
    setMaximumEnergy,
    remainingEnergy,
    ...props
}: EnergyInputProps) => {
    const { t } = useTranslation()

    return (
        <NumberInput
            required
            label={t("Quantité ({{quantity}} MWh restants)", {
                count: remainingEnergy,
                quantity: formatNumber(remainingEnergy),
            })}
            style={{ flex: 1 }}
            max={remainingEnergy}
            min={0}
            step={0.01}
            type="number"
            {...props}
            rightContent={
                <Button
                    label={t("Maximum")}
                    action={setMaximumEnergy}
                    variant="primary"
                />
            }
        />
    )
}
