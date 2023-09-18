
import { AxiosError } from "axios"
import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"
import Button, { ExternalLink } from "common/components/button"
import Dialog from "common/components/dialog"
import { Form, useForm } from "common/components/form"
import { AlertTriangle, Check, Plus, Return, Upload } from "common/components/icons"
import { FileInput } from "common/components/input"
import { useNotify } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import * as api from "../../api"



const ProvisionImporButton = () => {
    const portal = usePortal()
    const { t } = useTranslation()

    const showApplicationsChecker = () => {
        portal((close) => <ProvisionImportDialog onClose={close} />)
    }

    return (
        <Button
            asideX
            variant="primary"
            icon={Plus}
            label={t("Importer l’énergie à céder")}
            action={showApplicationsChecker}
        />
    )
}


type ProvisionImportDialogProps = {
    onClose: () => void
}

const ProvisionImportDialog = ({
    onClose,
}: ProvisionImportDialogProps) => {
    const { t } = useTranslation()
    const notify = useNotify()
    const entity = useEntity()

    const [missingCPO, setMissingCPO] = useState<string[] | undefined>(undefined) //TODO add test

    const { value, bind } = useForm({
        provisionCertificatesFile: undefined as File | undefined,
    })

    const importProvisionCertificates = useMutation(api.importProvisionCertificates, {
        invalidates: ["provision-certificates"],
        onError: (err) => {
            const error = (err as AxiosError<{ error: string, data: string[] }>).response?.data
            if (error?.error === "MISSING_CPO") {
                setMissingCPO(error.data)
            } else if (error?.error === "DB_INSERTION_ERROR") {
                notify(t("L'import excel a échoué. Assurez vous que certaines données n'aient pas déjà été importées."), { variant: "danger" })

            } else {
                notify(t("L'import excel a échoué"), { variant: "danger" })
            }
        },
        onSuccess: () => {
            notify(t("L'import excel a réussi"), { variant: "success" })
            onClose()
        }
    })

    function submitFiles() {
        if (!value.provisionCertificatesFile) return
        setMissingCPO(undefined)
        importProvisionCertificates.execute(
            entity.id,
            value.provisionCertificatesFile as File
        )
    }

    return (
        <Dialog onClose={onClose}>
            <header>
                <h1>{t("Importer l’énergie à céder")}</h1>
            </header>

            <main>
                <section>
                    <Form id="dc-checker">
                        <p>
                            {t(
                                "En tant qu’administrateur DGEC, vous pouvez importer ici des volumes d’énergie à céder, classé par trimestre et par aménageurs."
                            )}
                        </p>

                        <FileInput
                            loading={importProvisionCertificates.loading}
                            icon={value.provisionCertificatesFile ? Check : Upload}
                            label={t("Importer un fichier")}
                            placeholder="Choisir un fichier"
                            {...bind("provisionCertificatesFile")}
                        />

                        {missingCPO && missingCPO.length > 0 &&
                            <Alert variant="warning" icon={AlertTriangle} >
                                <section>
                                    <p>
                                        <strong>{t("Aménageurs manquants")} :</strong> <br />
                                        {t("Les aménageurs suivants ne sont pas sur CarbuRe :")}
                                    </p>
                                    <ul>
                                        {missingCPO.map((cpo) => <li key={cpo}>{cpo}</li>)}
                                    </ul>
                                    {t("Veuillez créer les entités ci-dessus sur CarbuRe dans l’interface d’aministrateur et ajouter à nouveau votre fichier d’énergie à céder.")}
                                    {" "}
                                    <ExternalLink href="/org/9/entities">
                                        Ajouter des sociétés
                                    </ExternalLink>

                                </section>
                            </Alert>
                        }


                    </Form>
                </section>
            </main>

            <footer>
                <Button
                    submit="dc-request"
                    loading={importProvisionCertificates.loading}
                    disabled={!value.provisionCertificatesFile}
                    variant="primary"
                    icon={Check}
                    action={submitFiles}
                    label={t("Importer")}
                />
                <Button icon={Return} action={onClose} label={t("Annuler")} />
            </footer>
        </Dialog>
    )
}

export default ProvisionImporButton
