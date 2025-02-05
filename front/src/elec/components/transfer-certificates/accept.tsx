import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Check, Return } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { ElecTransferCertificatesDetails } from "elec/types"
import { useTranslation } from "react-i18next"
import * as api from "../../api-operator"
import { useState } from "react"
import { RadioGroup } from "common/components/radio"
import { DateInput } from "common/components/input"
import css from "common/components/input.module.css"

interface AcceptTransferProps {
  transferCertificate?: ElecTransferCertificatesDetails
  onClose: () => void
  onAccepted: (
    usedInTiruert: boolean,
    consumptionDate: string | undefined
  ) => void
  tiruertChoice: boolean
}

export const AcceptTransfer = ({
  transferCertificate,
  onClose,
  onAccepted,
  tiruertChoice,
}: AcceptTransferProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const [usedInTiruert, setUsedInTiruert] = useState<string>(
    tiruertChoice ? "false" : "true"
  )
  const [consumptionDate, setConsumptionDate] = useState<string | undefined>(
    undefined
  )
  const [showConfirmationModal, setShowConfirmationModal] =
    useState<boolean>(false)

  const acceptTransfer = useMutation(api.acceptTransfer, {
    invalidates: [
      "elec-transfer-certificates",
      "elec-operator-snapshot",
      `nav-stats-${entity.id}`,
    ],
    onSuccess: () => {
      setShowConfirmationModal(false)
      notify(t("Le certificat de cession a été accepté"), {
        variant: "success",
      })
      onAccepted(usedInTiruert === "true", consumptionDate)
      onClose()
    },
  })

  const handleConfirmTransfer = async () => {
    if (transferCertificate) {
      await acceptTransfer.execute(
        entity.id,
        transferCertificate.id,
        usedInTiruert === "true",
        consumptionDate
      )
    }
  }

  const onAcceptTransfer = () => {
    setShowConfirmationModal(true)
  }

  const handleRadioChange = (value: string | undefined) => {
    if (value !== undefined) {
      setUsedInTiruert(value)
    }
  }

  const formatDate = (date: string | undefined) => {
    if (!date) return ""
    return new Date(date).toLocaleDateString("fr-FR")
  }

  return (
    <>
      <Dialog onClose={onClose}>
        <header>
          <h1>
            {t("Accepter le certificat n°")}
            {transferCertificate?.certificate_id ?? "..."}
          </h1>
        </header>

        <main>
          <section>
            {!tiruertChoice && (
              <p>
                {" "}
                {t("Ce certificat a été concerné par une déclaration TIRUERT")}
              </p>
            )}
            {tiruertChoice && (
              <p>
                {t(
                  "Est-ce que le certificat est concerné par une déclaration TIRUERT ?"
                )}
              </p>
            )}
            {tiruertChoice && (
              <RadioGroup
                options={[
                  { value: "true", label: t("Déclaration TIRUERT") },
                  { value: "false", label: t("Non concerné") },
                ]}
                value={usedInTiruert}
                onChange={handleRadioChange} // Use the new handler
                name="declaration-status"
              />
            )}

            {usedInTiruert === "true" && (
              <>
                <p>{t("J'indique la date de déclaration de la période :")}</p>
                <label className={css.label}>
                  Date de déclaration
                  <DateInput
                    value={consumptionDate}
                    onChange={setConsumptionDate}
                  />
                </label>
              </>
            )}
          </section>
        </main>

        <footer>
          <Button
            icon={Check}
            label={t("Accepter")}
            variant="success"
            disabled={
              !transferCertificate ||
              (usedInTiruert === "true" && consumptionDate === undefined)
            }
            action={onAcceptTransfer}
          />

          <Button icon={Return} label={t("Annuler")} action={onClose} />
        </footer>
      </Dialog>

      {showConfirmationModal && (
        <Dialog onClose={() => setShowConfirmationModal(false)}>
          <header>
            <h1>
              {t("Confirmer la déclaration du certificat n°")}
              {transferCertificate?.certificate_id ?? "..."}
            </h1>
          </header>
          <main>
            <p>
              {t(
                "Toute validation est définitive, votre certificat sera considéré comme consommé."
              )}
            </p>
            {usedInTiruert === "true" && (
              <p>
                {t(
                  "Ce certificat rentre dans le cadre d'une déclaration TIRUERT en date du {{consumptionDate}}.",
                  {
                    consumptionDate: formatDate(consumptionDate),
                  }
                )}
              </p>
            )}
          </main>
          <footer>
            <Button
              icon={Check}
              label={t("Confirmer")}
              variant="primary"
              action={() => {
                handleConfirmTransfer()
              }}
              loading={acceptTransfer.loading}
            />
          </footer>
        </Dialog>
      )}
    </>
  )
}
