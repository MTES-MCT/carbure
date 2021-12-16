import { Trans } from "react-i18next"

import { Entity } from "carbure/types"

import styles from "../components/form.module.css"

import useTransactionAdd from "../hooks/use-transaction-add"
import Modal from "common/components/modal"
import { AsyncButton, Button } from "common/components/button"
import { Plus, Return } from "common/components/icons"
import { StatusTitle } from "../components/status"
import TransactionForm from "../components/form"
import { useMatomo } from "matomo"

type TransactionAddProps = {
  entity: Entity
  refresh: () => void
}

const TransactionAdd = ({ entity, refresh }: TransactionAddProps) => {
  const matomo = useMatomo()

  const { form, request, change, submit, close } = useTransactionAdd(
    entity,
    refresh
  )

  return (
    <Modal onClose={close}>
      <StatusTitle editable>
        <Trans>Créer une nouvelle transaction</Trans>
      </StatusTitle>

      <TransactionForm
        id="transaction-add"
        entity={entity}
        transaction={form}
        error={request.error}
        onChange={change}
        onSubmit={() => {
          matomo.push(["trackEvent", "transactions", "create-batch"])
          submit()
        }}
      />

      <div className={styles.transactionFormButtons}>
        <AsyncButton
          submit="transaction-add"
          level="primary"
          icon={Plus}
          loading={request.loading}
        >
          <Trans>Créer lot</Trans>
        </AsyncButton>
        <Button
          icon={Return}
          className={styles.transactionNavButtons}
          onClick={close}
        >
          <Trans>Retour</Trans>
        </Button>
      </div>
    </Modal>
  )
}

export default TransactionAdd
