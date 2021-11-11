import cl from "clsx"
import useControlledState from "../hooks/controlled-state"
import Checkbox from "./checkbox"
import { multipleSelection } from "../utils/selection"
import { Normalizer } from "../utils/normalize"
import css from "./table.module.css"
import { Col, LoaderOverlay } from "./scaffold"

export interface TableProps<T> {
  className?: string
  style?: React.CSSProperties
  loading?: boolean
  headless?: boolean
  columns: Column<T>[]
  rows: T[]
  order?: Order
  onOrder?: (order: Order | undefined) => void
  onAction?: (value: T) => void
}

export function Table<T>({
  className,
  style,
  loading,
  headless,
  columns,
  rows,
  order: controlledOrder,
  onOrder,
  onAction,
}: TableProps<T>) {
  const { order, orderBy } = useOrderBy(controlledOrder, onOrder)
  const compare = useCompare(columns, order)

  return (
    <div data-list className={cl(css.table, className)} style={style}>
      {!headless && (
        <header className={css.columns}>
          {columns.map((column, i) => (
            <div
              key={column.key ?? i}
              data-sortable={column.key ? true : undefined}
              onClick={column.key ? () => orderBy(column.key!) : undefined}
              title={
                typeof column.header === "string" ? column.header : undefined
              }
              className={cl(
                css.header,
                column.className,
                column.small && css.small
              )}
            >
              {column.header}
              {order && column.key === order.column && (
                <span>{order.direction === "asc" ? " ▲" : " ▼"}</span>
              )}
            </div>
          ))}
        </header>
      )}

      <ul className={css.rows}>
        {[...rows].sort(compare).map((row, i) => (
          <li key={i} onClick={onAction ? () => onAction(row) : undefined}>
            {columns.map((column, i) => (
              <div
                key={column.key ?? i}
                className={cl(
                  css.cell,
                  column.className,
                  column.small && css.small
                )}
              >
                {column.cell(row)}
              </div>
            ))}
          </li>
        ))}
      </ul>

      {loading && <LoaderOverlay />}
    </div>
  )
}

export function selectionColumn<T>(
  rows: T[],
  selected: T[],
  onSelect: (selected: T[]) => void,
  normalize?: Normalizer<T>
): Column<T> {
  const selection = multipleSelection(selected, onSelect, normalize)

  return {
    className: css.selection,
    header: (
      <Checkbox
        value={selection.isAllSelected(rows)}
        onChange={() => selection.onSelectAll(rows)}
      />
    ),
    cell: (value) => (
      <Checkbox
        value={selection.isSelected(value)}
        onChange={() => selection.onSelect(value)}
      />
    ),
  }
}

export type MarkerVariant = "info" | "success" | "warning" | "danger"
export type Marker<T> = (value: T) => MarkerVariant | undefined

export function markerColumn<T>(mark: Marker<T>): Column<T> {
  return {
    className: css.marker,
    cell: (value) => {
      const variant = mark(value)
      return variant ? <div className={css[variant]} /> : null
    },
  }
}

export function actionColumn<T>(
  actions: (value: T) => React.ReactElement[]
): Column<T> {
  return {
    className: css.actions,
    cell: (value) => actions(value).map((e, key) => ({ ...e, key })),
  }
}

export interface Order {
  column: string
  direction: "asc" | "desc"
}

export function useOrderBy(
  orderControlled?: Order | undefined,
  setOrderControlled?: (order: Order | undefined) => void
) {
  const [order, setOrder] = useControlledState<Order | undefined>(
    undefined,
    orderControlled,
    setOrderControlled
  )

  function orderBy(column: string) {
    if (!order || column !== order.column) {
      setOrder({ column, direction: "asc" })
    } else if (column === order.column) {
      if (order.direction === "asc") {
        setOrder({ column, direction: "desc" })
      } else {
        setOrder(undefined)
      }
    }
  }

  return { order, orderBy }
}

const collator = new Intl.Collator([], { numeric: true })
export function useCompare<T>(columns: Column<T>[], order: Order | undefined) {
  const column = columns.find(({ key }) => key && key === order?.column)

  return function compare(a: T, b: T) {
    if (!order || !column || !column.orderBy) return 0

    const direction = order.direction === "asc" ? 1 : -1
    const referenceA = column.orderBy(a).toString()
    const referenceB = column.orderBy(b).toString()
    return direction * collator.compare(referenceA, referenceB)
  }
}

export interface Column<T> {
  cell: (value: T) => React.ReactNode
  header?: React.ReactNode
  key?: string
  className?: string
  small?: boolean
  orderBy?: OrderBy<T>
}

export type OrderBy<T> = (value: T) => number | string

export interface CellProps {
  text: string | number
  sub?: string | number
}

export const Cell = ({ text, sub }: any) => (
  <Col>
    <strong title={text}>{text || sub}</strong>
    {text && sub !== undefined && <small title={sub}>{sub}</small>}
  </Col>
)

export default Table
