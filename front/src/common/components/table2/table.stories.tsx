import type { Meta, StoryObj } from "@storybook/react"
import { Cell, Column, Table } from "./table"

const rows = [
  {
    name: "John Doe",
    age: 30,
    email: "john.doe@example.com",
  },
  {
    name: "Jane Doe",
    age: 25,
    email: "jane.doe@example.com",
  },
  {
    name: "John Smith",
    age: 35,
    email: "john.smith@example.com",
  },
]
const columnName: Column<(typeof rows)[number]> = {
  header: "Name",
  cell: (row) => <Cell text={row.name} />,
}
const columnAge: Column<(typeof rows)[number]> = {
  header: "Age",
  cell: (row) => <Cell text={row.age} />,
}
const columnEmail: Column<(typeof rows)[number]> = {
  header: "Email",
  cell: (row) => <Cell text={row.email} />,
}

const columns: Column<(typeof rows)[number]>[] = [
  columnName,
  columnAge,
  columnEmail,
]

const meta: Meta<typeof Table<(typeof rows)[number]>> = {
  component: Table,
  title: "common/components/Table",
  args: {
    rows,
    columns,
  },
}

type Story = StoryObj<typeof Table<(typeof rows)[number]>>

export default meta

export const Default: Story = {}

export const WithOrder: Story = {
  args: {
    columns: [
      {
        ...columnName,
        key: "name",
        orderBy: (row) => row.name,
      },
      columnAge,
      columnEmail,
    ],
  },
}
