import { useTranslation } from 'react-i18next'
import { LotUpdate } from 'common/types'
import { Edit } from 'common/components/icons'
import Table, { Column } from 'common/components/table'
import { Collapsible } from 'common/components/alert'
import { formatDate } from "settings/components/common"
import { padding } from './list-columns'
import styles from './history.module.css'

type TransactionHistoryProps = {
  history: LotUpdate[] | undefined
}

const columns: Column<LotUpdate>[] = [
  padding,
  {
    header: 'Date',
    render: u => formatDate(u.datetime, true),
  },
  {
    header: 'Champ modifié',
    render: u => u.label ?? u.field,
  },
  {
    header: 'Valeur',
    render: u => (
      <div>
        {u.value_after && <span style={{ marginRight: 12}}>{u.value_after}</span>}
        <span style={{fontWeight: 'normal', textDecoration: 'line-through'}}>{u.value_before}</span>
      </div>
    )
  },
  
  {
    header: 'Modifié par',
    render: u => u.modified_by
  },
  padding,
]

const TransactionHistory = ({ history = [] }: TransactionHistoryProps) => {
  const { t } = useTranslation()
  const { t:tFields } = useTranslation('fields')

  const rows = history
    .filter(h => tFields(h.field) != h.field) // ignore fields that have no translation
    .map(value => ({ value: { ...value, label: tFields(value.field) } }))
  
  return ( 
    <Collapsible icon={Edit} title={t("Historique des corrections")} className={styles.history}>
      <Table 
        columns={columns}
        rows={rows}
        className={styles.historyTable}
      />
    </Collapsible>
  )
}

export default TransactionHistory