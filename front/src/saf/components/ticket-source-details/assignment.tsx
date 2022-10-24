import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import Form, { Fieldset, useForm } from "common/components/form"
import { useHashMatch } from "common/components/hash-route"
import { Return, Send, Split } from "common/components/icons"
import { DateInput, NumberInput, TextInput } from "common/components/input"
import Portal from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useMutation, useQuery } from "common/hooks/async"
import { invalidate } from "common/hooks/invalidate"
import { formatDate, formatNumber } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import { safTicketSourceDetails } from "saf/__test__/data"
import * as api from "../../api"
import TicketSourceTag from "../ticket-sources/tag"
import TicketSourceFields from "./fields"
import Collapse from "common/components/collapse"
import {
  LotPreview,
  SafTicketAssignementQuery,
  SafTicketPreview,
  SafTicketSource,
  SafTicketSourceDetails,
} from "saf/types"
import { useEffect, useRef, useState } from "react"
import NavigationButtons from "transaction-details/components/lots/navigation"
import TicketTag from "../tickets/tag"
import { cp } from "fs/promises"
import Autocomplete from "common/components/autocomplete"
import { findEntities } from "carbure/api"
import * as norm from "carbure/utils/normalizers"
import { Entity } from "carbure/types"

export interface TicketAssignmentProps {
  ticketSource: SafTicketSourceDetails
  onClose: () => void
}
export const TicketAssignment = ({
  ticketSource,
  onClose,
}: TicketAssignmentProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const [client, setClient] = useState<Entity | string | undefined>()

  const { value, bind, setField, errors } = useForm<
    Partial<SafTicketAssignementQuery>
  >({
    volume: 0,
    client_id: undefined,
    agreement_reference: undefined,
    agreement_date: undefined,
  })

  // errors.volume = "test"
  const remainingVolume =
    ticketSource.total_volume - ticketSource.assigned_volume

  const closeDialog = () => {
    onClose()
  }

  const assignSafTicket = useMutation(api.assignSafTicket, {
    invalidates: ["ticket-source-details"],
  })

  const assignTicket = async () => {
    console.log("ok")
    errors.volume = "test"
    // await assignSafTicket.execute(
    //   entity.id,
    //   value.volume as number,
    //   client?.id as number,
    //   value.agreement_reference as string,
    //   value.agreement_date as string
    // )
  }

  const setMaximumVolume = () => {
    setField("volume", remainingVolume)
  }

  const findSafClient = (query: string) => {
    return findEntities(query)
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog}>
        <header>
          <h1>
            {t("Affecter le volume CAD n°")}
            {ticketSource?.carbure_id}
          </h1>
        </header>

        <main>
          <section>
            <p>
              {t(
                "Veuillez remplir le formulaire ci-dessous afin d’affecter une partie ou tout le volume du lot à un client et générer un ticket de Carburant Durable d'Aviation"
              )}
            </p>

            <Form id="assign-ticket" onSubmit={assignTicket}>
              <div
                style={{
                  display: "flex",
                  alignItems: "end",
                }}
              >
                <NumberInput
                  // error={{ error: "tu peux pas" }}
                  required
                  label={t("Volume ({{volume}} litres disponibles)", {
                    count: remainingVolume,
                    volume: formatNumber(remainingVolume),
                  })}
                  style={{ flex: 1 }}
                  max={remainingVolume}
                  min={0}
                  type="number"
                  {...bind("volume")}
                  // icon={
                  //   <Button
                  //     label={t("Maximum")}
                  //     action={setMaximumVolume}
                  //     variant="primary"
                  //   />
                  // }
                />
                <Button
                  // style={{ height: "max-content" }}
                  label={t("Maximum")}
                  action={setMaximumVolume}
                  variant="primary"
                />
              </div>

              <Autocomplete
                required
                label={t("Client")}
                getOptions={findSafClient}
                onChange={setClient}
                value={client}
                normalize={norm.normalizeEntityOrUnknown}
                // create={norm.identity}
                // {...bind("client_id")}
              />

              <TextInput
                label={t("N° de Contrat (facture ou bon de commande)")}
                {...bind("agreement_reference")}
              />

              <DateInput
                label={t("Date du contrat (facture ou du bon de commande )")}
                {...bind("agreement_date")}
              />
            </Form>
          </section>
        </main>

        <footer>
          <Button
            icon={Send}
            label={t("Affecter")}
            variant="primary"
            submit="assign-ticket"
          />

          <Button icon={Return} label={t("Retour")} action={closeDialog} />
        </footer>
      </Dialog>
    </Portal>
  )
}

export default TicketAssignment
