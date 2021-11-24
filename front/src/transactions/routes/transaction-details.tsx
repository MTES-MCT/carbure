import React from "react"
import { Trans, useTranslation } from "react-i18next"

import { LotStatus, EntityType, UserRole, Transaction } from "common/types"
import { Entity } from "carbure/types"
import { LotDeleter } from "transactions/hooks/actions/use-delete-lots"
import { LotAcceptor } from "transactions/hooks/actions/use-accept-lots"
import { LotRejector } from "transactions/hooks/actions/use-reject-lots"
import { LotValidator } from "transactions/hooks/actions/use-validate-lots"
import { LotAdministrator } from "transactions/hooks/actions/use-admin-lots"

import styles from "../components/form.module.css"

import useTransactionDetails from "../hooks/use-transaction-details"
import useNavigation from "../hooks/query/use-navigate"

import {
  AlertTriangle,
  Check,
  Cross,
  Return,
  Save,
  ChevronLeft,
  ChevronRight,
  Edit,
  EyeOff,
  Pin,
  PinOff,
  Eye,
} from "common/components/icons"
import { Box, LoaderOverlay } from "common/components"
import { AsyncButton, Button } from "common/components/button"
import Modal from "common/components/modal"
import TransactionForm from "../components/form"
import { StatusTitle } from "../components/status"
import Comments from "../components/form-comments"
import ValidationErrors from "../components/form-errors"
import TransactionHistory from "../components/history"
import { useRights } from "carbure/hooks/entity"
import { LotAuditor } from "transactions/hooks/actions/use-audits"
import { useMatomo } from "matomo"

const EDITABLE = [LotStatus.Draft, LotStatus.ToFix]
const COMMENTABLE = [LotStatus.ToFix, LotStatus.Inbox]

type TransactionDetailsProps = {
  entity: Entity
  deleter: LotDeleter
  validator: LotValidator
  acceptor: LotAcceptor
  rejector: LotRejector
  administrator: LotAdministrator
  auditor: LotAuditor
  transactions: number[]
  refresh: () => void
}

const TransactionDetails = ({
  entity,
  deleter,
  validator,
  acceptor,
  rejector,
  administrator,
  auditor,
  transactions,
  refresh,
}: TransactionDetailsProps) => {
  const {
    form,
    hasChange,
    details,
    request,
    comment,
    status,
    fieldErrors,
    validationErrors,
    transaction,
    change,
    submit,
    close,
    addComment,
    addControlComment,
    refreshDetails,
  } = useTransactionDetails(entity, refresh)

  const { t } = useTranslation()
  const matomo = useMatomo()

  const rights = useRights()
  const navigator = useNavigation(transactions)

  const history = details.data?.updates?.filter(
    (h) => t(h.field, { ns: "fields" }) !== h.field
  )

  const isEditable = EDITABLE.includes(status)
  const isCommentable = COMMENTABLE.includes(status)

  const isAdmin = entity?.entity_type === EntityType.Administration
  const isAuditor = entity?.entity_type === EntityType.Auditor

  const isAuthor =
    Boolean(entity) && transaction?.lot.added_by?.id === entity?.id
  const isVendor =
    Boolean(entity) && transaction?.carbure_vendor?.id === entity!.id

  const hasErrors =
    validationErrors.length > 0 || Object.keys(fieldErrors).length > 0

  const canModify = rights.is(UserRole.Admin, UserRole.ReadWrite)

  async function run(
    action: (tx: Transaction) => Promise<boolean>,
    nextOnDone: boolean = false
  ) {
    if (transaction && (await action(transaction))) {
      refreshDetails()

      if (nextOnDone) {
        navigator.next()
      }
    }
  }

  return (
    <Modal onClose={close}>
      <StatusTitle editable={isEditable} details={details.data} entity={entity}>
        <Trans>Détails de la transaction {{ id: form.carbure_id }}</Trans>
      </StatusTitle>

      <TransactionForm
        id="transaction-details"
        entity={entity}
        readOnly={!isEditable || !canModify}
        transaction={form}
        error={details.error ?? request.error}
        errors={fieldErrors}
        onChange={change}
      />

      {hasErrors && <ValidationErrors errors={validationErrors} />}

      {details.data && details.data.comments.length > 0 && (
        <Comments
          title={t("Commentaires")}
          readOnly={!isCommentable}
          loading={comment.loading}
          comments={details.data.comments}
          onComment={addComment}
        />
      )}

      {details.data?.admin_comments &&
        details.data.admin_comments.length > 0 && (
          <Comments
            title={t("Notes d'audits")}
            loading={comment.loading}
            comments={details.data.admin_comments}
            onComment={addControlComment}
            role={isAdmin ? "admin" : "auditor"}
          />
        )}

      {Boolean(history?.length) && <TransactionHistory history={history} />}

      <div className={styles.transactionFormButtons}>
        {canModify && isEditable && (
          <AsyncButton
            disabled={!hasChange}
            submit="transaction-details"
            icon={Save}
            level="primary"
            loading={request.loading}
            onClick={submit}
          >
            <Trans>Sauvegarder</Trans>
          </AsyncButton>
        )}

        {canModify && status === LotStatus.Draft && (
          <AsyncButton
            disabled={hasChange}
            icon={Check}
            level="success"
            loading={validator.loading}
            onClick={() => run(validator.validateLot)}
          >
            <Trans>Envoyer</Trans>
          </AsyncButton>
        )}

        {canModify && status === LotStatus.ToFix && (
          <AsyncButton
            disabled={hasChange}
            icon={Check}
            level="success"
            loading={validator.loading}
            onClick={() => run(validator.validateAndCommentLot)}
          >
            <Trans>Renvoyer</Trans>
          </AsyncButton>
        )}

        {canModify && isEditable && (
          <AsyncButton
            icon={Cross}
            level="danger"
            loading={deleter.loading}
            onClick={() => run(deleter.deleteLot, true)}
          >
            <Trans>Supprimer</Trans>
          </AsyncButton>
        )}

        {canModify &&
          status === LotStatus.Inbox &&
          transaction?.delivery_status !== "AC" && (
            <React.Fragment>
              <AsyncButton
                icon={Check}
                level="success"
                loading={acceptor.loading}
                onClick={() => {
                  matomo.push(["trackEvent", "transactions", "accept-batch"])
                  run(acceptor.acceptLot)
                }}
              >
                <Trans>Accepter</Trans>
              </AsyncButton>

              {!transaction?.lot.parent_lot && (
                <AsyncButton
                  icon={AlertTriangle}
                  level="warning"
                  loading={acceptor.loading}
                  onClick={() => {
                    matomo.push(["trackEvent", "transactions", "ask-batch-correction"]) // prettier-ignore
                    run(acceptor.acceptAndCommentLot)
                  }}
                >
                  <Trans>Accepter sous réserve</Trans>
                </AsyncButton>
              )}

              <AsyncButton
                icon={Cross}
                level="danger"
                loading={rejector.loading}
                onClick={() => {
                  matomo.push(["trackEvent", "transactions", "reject-batch"])
                  run(rejector.rejectLot, true)
                }}
              >
                <Trans>Refuser</Trans>
              </AsyncButton>
            </React.Fragment>
          )}

        {canModify &&
          (isVendor || isAuthor) &&
          !isAdmin &&
          !isAuditor &&
          [LotStatus.Accepted, LotStatus.Declaration].includes(status) && (
            <AsyncButton
              icon={Edit}
              level="warning"
              loading={acceptor.loading}
              onClick={() => {
                matomo.push(["trackEvent", "transactions", "amend-batch"])
                run(acceptor.amendLot)
              }}
            >
              <Trans>Corriger</Trans>
            </AsyncButton>
          )}

        {canModify &&
          !isVendor &&
          !isAdmin &&
          !isAuditor &&
          !isAuthor &&
          [LotStatus.Accepted, LotStatus.Declaration].includes(status) && (
            <AsyncButton
              icon={Edit}
              level="warning"
              loading={acceptor.loading}
              onClick={() => {
                matomo.push(["trackEvent", "transactions", "ask-batch-correction"]) // prettier-ignore
                run(acceptor.askForCorrection)
              }}
            >
              <Trans>Demander une correction</Trans>
            </AsyncButton>
          )}

        {isAdmin && (
          <React.Fragment>
            <AsyncButton
              icon={transaction?.highlighted_by_admin ? PinOff : Pin}
              level="success"
              loading={administrator.loading}
              onClick={() => run(administrator.markForReview, true)}
            >
              {transaction?.highlighted_by_admin
                ? t("Désépingler le lot")
                : t("Épingler le lot")}
            </AsyncButton>
            <AsyncButton
              icon={transaction?.hidden_by_admin ? Eye : EyeOff}
              level="warning"
              loading={administrator.loading}
              onClick={() => run(administrator.markAsRead, true)}
            >
              {transaction?.hidden_by_admin
                ? t("Montrer le lot")
                : t("Ignorer le lot")}
            </AsyncButton>
            <AsyncButton
              icon={Cross}
              level="danger"
              loading={administrator.loading}
              onClick={() => run(administrator.deleteLot, true)}
            >
              <Trans>Supprimer le lot</Trans>
            </AsyncButton>
          </React.Fragment>
        )}

        {isAuditor && (
          <React.Fragment>
            <AsyncButton
              icon={transaction?.highlighted_by_auditor ? PinOff : Pin}
              level="success"
              loading={auditor.loading}
              onClick={() => run(auditor.highlightLot, true)}
            >
              {transaction?.highlighted_by_auditor
                ? t("Désépingler le lot")
                : t("Épingler le lot")}
            </AsyncButton>
            <AsyncButton
              icon={transaction?.hidden_by_auditor ? Eye : EyeOff}
              level="warning"
              loading={auditor.loading}
              onClick={() => run(auditor.hideLot, true)}
            >
              {transaction?.hidden_by_auditor
                ? t("Montrer le lot")
                : t("Ignorer le lot")}
            </AsyncButton>
          </React.Fragment>
        )}

        <Box row className={styles.transactionNavButtons}>
          <Button
            icon={ChevronLeft}
            disabled={!navigator.hasPrev}
            onClick={navigator.prev}
          >
            <Trans>Lot Précédent</Trans>
          </Button>

          <Button
            icon={ChevronRight}
            disabled={!navigator.hasNext}
            onClick={navigator.next}
          >
            <Trans>Lot Suivant</Trans>
          </Button>

          <Button icon={Return} onClick={close}>
            <Trans>Retour</Trans>
          </Button>
        </Box>
      </div>

      {details.loading && <LoaderOverlay />}
    </Modal>
  )
}

export default TransactionDetails
