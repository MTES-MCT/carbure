import { Fragment, useState } from 'react'
import { useTranslation, Trans } from 'react-i18next'
import { DoubleCounting } from 'common/types'
import { LoaderOverlay } from 'common/components'
import Tabs from 'common/components/tabs'
import Table, { Column } from 'common/components/table'
import { padding } from 'transactions/components/list-columns'
import { Alert } from 'common/components/alert'
import { AlertCircle } from 'common/components/icons'
import { AgreementsOverview } from '../api'
import { formatDate } from 'settings/components/common'
import { DoubleCountingPrompt } from './agreement-details'
import { prompt } from 'common/components/dialog'

type AgreementListProps = {
  agreements: AgreementsOverview | null
}

const AgreementList = ({ agreements }: AgreementListProps) => {
  const { t } = useTranslation()
  const [tab, setTab] = useState('pending')
  
  const tabs = [
    { key: 'pending', label: t('En attente') },
    { key: 'accepted', label: t('Accepté') },
    { key: 'expired', label: t('Expiré') },
    { key: 'rejected', label: t('Refusé') },
  ]

  if (agreements === null) return <LoaderOverlay />

  const columns: Column<DoubleCounting>[] = [
    padding,
    { header: t('Entité'), render: (a) => a.producer.name },
    { header: t('Site de production'), render: (a) => a.production_site },
    { header: t('Période de validité'), render: (a) => `${formatDate(a.period_start)} ▸ ${formatDate(a.period_end)}` },
    padding
  ]

  const agreementRowMapper = (agreement: DoubleCounting) => ({
    value: agreement,
    onClick: () => prompt((resolve) => <DoubleCountingPrompt agreementID={agreement.id} onResolve={resolve} />)
  })

  return (
    <div style={{padding: '8px 120px'}}>
      <Tabs tabs={tabs} focus={tab} onFocus={setTab} />
      
      {tab === 'pending' && (
        <Fragment>
          {agreements.pending.count === 0 && (
            <Alert level="warning" icon={AlertCircle}>
              <Trans>
                Aucun dossier en attente trouvé
              </Trans>
            </Alert>
          )}

          {agreements.pending.count > 0 && (
            <Table 
              columns={columns} 
              rows={agreements.pending.agreements.map(agreementRowMapper)}
            />
          )}
        </Fragment>
      )}

      {tab === 'accepted' && (
        <Fragment>
          {agreements.accepted.count === 0 && (
            <Alert level="warning" icon={AlertCircle}>
              <Trans>
                Aucun dossier accepté trouvé
              </Trans>
            </Alert>
          )}

          {agreements.accepted.count > 0 && (
            <Table 
              columns={columns} 
              rows={agreements.accepted.agreements.map(agreementRowMapper)}
            />
          )}
        </Fragment>
      )}

      {tab === 'expired' && (
        <Fragment>
          {agreements.expired.count === 0 && (
            <Alert level="warning" icon={AlertCircle}>
              <Trans>
                Aucun dossier expiré trouvé
              </Trans>
            </Alert>
          )}

          {agreements.expired.count > 0 && (
            <Table 
              columns={columns} 
              rows={agreements.expired.agreements.map(agreementRowMapper)}
            />
          )}
        </Fragment>
      )}

      {tab === 'rejected' && (
        <Fragment>
          {agreements.rejected.count === 0 && (
            <Alert level="warning" icon={AlertCircle}>
              <Trans>
                Aucun dossier refusé trouvé
              </Trans>
            </Alert>
          )}

          {agreements.rejected.count > 0 && (
            <Table 
              columns={columns} 
              rows={agreements.rejected.agreements.map(agreementRowMapper)}
            />
          )}
        </Fragment>
      )}
    </div>
  )
}

export default AgreementList