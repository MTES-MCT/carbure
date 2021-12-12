import cl from "clsx"
import useControlledState from "../hooks/controlled-state"
import Checkbox from "./checkbox"
import { multipleSelection } from "../utils/selection"
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
              {order && column.key === order.column && (
                <span>{order.direction === "asc" ? " ▲" : " ▼"}</span>
              )}{" "}
              {column.header}
            </div>
          ))}
        </header>
      )}

      <ul className={css.rows}>
        {[...rows].sort(compare).map((row, i) => (
          <li
            key={i}
            data-interactive={onAction ? true : undefined}
            onClick={onAction ? () => onAction(row) : undefined}
          >
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

export function selectionColumn<T, V>(
  rows: T[],
  selected: V[],
  onSelect: (selected: V[]) => void,
  identify: (item: T) => V
): Column<T> {
  const values = rows.map(identify)
  const selection = multipleSelection(selected, onSelect)

  return {
    className: css.selection,
    header: (
      <Checkbox
        captive
        value={selection.isAllSelected(values)}
        onChange={() => selection.onSelectAll(values)}
      />
    ),
    cell: (item) => (
      <Checkbox
        captive
        value={selection.isSelected(identify(item))}
        onChange={() => selection.onSelect(identify(item))}
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
    const referenceA = column.orderBy(a)
    const referenceB = column.orderBy(b)

    if (typeof referenceA === 'number' && typeof referenceB === 'number') {
      return direction * (referenceA - referenceB);
    } else {
      return direction * collator.compare(referenceA.toString(), referenceB.toString())
    }
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

export type OrderBy<T> = (value: T) => string | number

export type CellVariant = "warning"
export interface CellProps {
  variant?: CellVariant
  icon?: React.FunctionComponent | React.ReactNode
  text?: any
  sub?: any
}

export const Cell = ({ variant, icon: Icon, text, sub }: CellProps) => {
  const icon = typeof Icon === "function" ? <Icon /> : Icon

  return (
    <Col className={cl(variant && css[variant])}>
      <strong title={`${text}`}>
        {text || sub} {icon}
      </strong>
      {text && sub !== undefined && <small title={`${sub}`}>{sub}</small>}
    </Col>
  )
}

export default Table
