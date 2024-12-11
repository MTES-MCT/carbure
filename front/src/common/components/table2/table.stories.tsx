import type { Meta, StoryObj } from "@storybook/react"
import { Cell, Column, Table } from "./table"
import { useState } from "react"
import { Button } from "../button2"

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

export const Loading: Story = {
  args: {
    loading: true,
  },
  parameters: {
    chromatic: { disableSnapshot: true },
  },
}

export const LinkRows: Story = {
  args: {
    rowLink: (row) => `/${row.age}`,
  },
}

export const HiddenColumns: Story = {
  args: {
    columns: [columnName, { ...columnAge, hidden: true }, columnEmail],
  },
}

export const SelectableRows: Story = {
  args: {
    columns: [columnName, columnAge, columnEmail],
    hasSelectionColumn: true,
    onSelect: () => {},
    identify: (row) => row.age,
  },
  render: (args) => {
    const [selected, setSelected] = useState<number[]>(args.selected ?? [])
    return <Table {...args} selected={selected} onSelect={setSelected} />
  },
}

export const OneRowSelected: Story = {
  ...SelectableRows,
  args: {
    columns: [columnName, columnAge, columnEmail],
    hasSelectionColumn: true,
    selected: [35],
    onSelect: () => {},
    identify: (row) => row.age,
    topActions: [
      <Button priority="tertiary no outline" iconId="fr-icon-survey-fill">
        First action
      </Button>,
      <Button
        priority="tertiary no outline"
        iconId="fr-icon-survey-fill"
        style={{ color: "green" }}
      >
        First action
      </Button>,
    ],
  },
}
