import cl from "clsx"
import { Link, To } from "react-router-dom"
import useControlledState from "../../hooks/controlled-state"
import { multipleSelection } from "../../utils/selection"
import { ChevronRight } from "../icons"
import { Col, LoaderOverlay } from "../scaffold"
import css from "./table.module.css"
import Tooltip from "../tooltip"
import { Text } from "../text"
import { useTranslation } from "react-i18next"
import { Checkbox } from "../inputs2"
import { ReactNode } from "react"

export type TableVariant = "spaced" | "compact"

export interface TableProps<T> {
  className?: string
  style?: React.CSSProperties
  variant?: TableVariant
  loading?: boolean
  headless?: boolean
  // If true, the table will have a selection column
  hasSelectionColumn?: boolean
  columns: Column<T>[]
  rows: T[]
  order?: Order

  // List of selected rows
  selected?: number[]

  // Callback to update the list of selected rows
  onSelect?: (selected: number[]) => void

  // Function that determines if a row is selected by comparing its identifier with the array of selected values
  identify?: (item: T) => number

  // Actions to display at the top of the table when there are selected rows
  topActions?: React.ReactNode[]

  onOrder?: (order: Order | undefined) => void
  onAction?: (value: T, index: number) => void
  rowProps?: (row: T, i?: number) => JSX.IntrinsicElements["li"]
  rowLink?: (row: T) => To
}

export function Table<T>({
  className,
  style,
  variant,
  loading,
  headless,
  hasSelectionColumn,
  selected = [],
  topActions,
  identify,
  columns: _columns,
  rows,
  order: controlledOrder,
  rowProps,
  rowLink,
  onOrder,
  onAction,
  onSelect,
}: TableProps<T>) {
  const columns =
    hasSelectionColumn && onSelect && identify
      ? [selectionColumn(rows, selected, onSelect, identify), ..._columns]
      : _columns

  const { order, orderBy } = useOrderBy(controlledOrder, onOrder)
  const compare = useCompare(columns, order)
  const { t } = useTranslation()
  return (
    <div
      data-list
      // data-headless={headless ? "" : undefined} //TODO check if this not cause trouble / I remove to avoid overlap gap in table
      className={cl(css.table, variant && css[variant], className)}
      style={style}
    >
      {!headless && (
        <header
          className={cl(css.columns, selected.length > 0 && css.topActions)}
        >
          {selected.length > 0 ? (
            <>
              <span
                className={cl(
                  css["top-actions__count"],
                  css["top-actions__item"]
                )}
              >
                <Checkbox
                  captive
                  value={selected.length > 0}
                  onChange={() => onSelect?.([])}
                  small
                  style={{ marginRight: "8px" }}
                />
                {t("{{count}} lignes sélectionnées", {
                  count: selected.length,
                })}
              </span>
              {topActions?.map((action, i) => (
                <div
                  className={css["top-actions__item"]}
                  key={`top-actions-item${i}`}
                >
                  {action}
                </div>
              ))}
            </>
          ) : (
            columns.filter(isVisible).map((column, i) => (
              <Text
                is="div"
                key={column.key ?? i}
                data-sortable={column.key ? true : undefined}
                componentProps={{
                  onClick: column.key ? () => orderBy(column.key!) : undefined,
                  title:
                    typeof column.header === "string"
                      ? column.header
                      : undefined,
                }}
                style={column.style}
                className={cl(
                  css.header,
                  column.className,
                  column.small && css.small
                )}
                size="sm"
                fontWeight="bold"
              >
                {column.key && (
                  <span
                    className={cl(column.key !== order?.column && css.sortable)}
                  >
                    {column.key !== order?.column || order?.direction === "asc"
                      ? " ▲"
                      : " ▼"}
                  </span>
                )}{" "}
                {column.header}
              </Text>
            ))
          )}
        </header>
      )}
      <ul className={css.rows}>
        {[...rows].sort(compare).map((row, i) => {
          const props = rowProps?.(row, i) ?? {}
          const link = rowLink?.(row)

          const cells = columns.filter(isVisible).map((column, i) => (
            <div
              key={column.key ?? i}
              style={column.style}
              className={cl(
                css.cell,
                column.className,
                column.small && css.small
              )}
            >
              {column.cell(row)}
            </div>
          ))

          return (
            <li
              key={i}
              {...props}
              className={cl(link && css.rowLink)}
              data-interactive={onAction ? true : undefined}
              onClick={onAction ? () => onAction(row, i) : undefined}
            >
              {link ? (
                <Link to={link} className={css.rowLink}>
                  {cells}
                </Link>
              ) : (
                cells
              )}
            </li>
          )
        })}
      </ul>
      {loading && <LoaderOverlay />}
    </div>
  )
}

function isVisible(column: Column<any>) {
  return !column.hidden
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
        small
      />
    ),
    cell: (item) => (
      <Checkbox
        captive
        value={selection.isSelected(identify(item))}
        onChange={() => {
          console.log("on change", item)
          selection.onSelect(identify(item))
        }}
        small
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
    cell: (value) => {
      const buttons = actions(value).map((e, key) => ({ ...e, key }))
      if (buttons.length === 0) return <ChevronRight color="var(--gray-dark)" />
      else return <>{buttons}</>
    },
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

    if (typeof referenceA === "number" && typeof referenceB === "number") {
      return direction * (referenceA - referenceB)
    } else {
      return (
        direction *
        collator.compare(referenceA.toString(), referenceB.toString())
      )
    }
  }
}

export interface Column<T> {
  cell: (value: T) => React.ReactNode
  header?: React.ReactNode
  key?: string
  className?: string
  style?: React.CSSProperties
  small?: boolean
  hidden?: boolean
  orderBy?: OrderBy<T>
}

export type OrderBy<T> = (value: T) => string | number

export type CellVariant = "warning"
export interface CellProps {
  className?: string
  style?: React.CSSProperties
  variant?: CellVariant
  icon?: React.FunctionComponent | React.ReactNode
  text?: ReactNode
  sub?: ReactNode
}

export const Cell = ({
  variant,
  className,
  style,
  icon: Icon,
  text,
  sub,
}: CellProps) => {
  const icon = typeof Icon === "function" ? <Icon /> : Icon

  return (
    <Col
      className={cl(
        css.overflow,
        text && sub && css.multiline,
        variant && css[variant],
        className
      )}
      style={style}
    >
      <Tooltip title={`${text || sub}`}>
        <Text is="span" size={text && sub ? "sm" : undefined}>
          {text || sub}
          {icon}
        </Text>
      </Tooltip>
      {text && sub !== undefined && (
        <Text is="span" size="sm" className={css["cell__sub-text"]}>
          {sub}
        </Text>
      )}
    </Col>
  )
}

export default Table
