import type { Meta, StoryObj } from "@storybook/react"

import { PrivateNavigation } from "./private-navigation"
import {
  PrivateNavigationProvider,
  usePrivateNavigation,
} from "./private-navigation.context"
import { EntityType } from "carbure/types"
import { mockGetWithResponseData, mockUser } from "carbure/__test__/helpers"
import { reactRouterParameters } from "storybook-addon-remix-react-router"
import { ExtAdminPagesEnum } from "api-schema"
import { apiTypes } from "common/services/api-fetch.types"

const meta: Meta<typeof PrivateNavigation> = {
  component: PrivateNavigation,
  title: "common/layouts/navigation/private",
  decorators: [
    (Story) => (
      <PrivateNavigationProvider>
        <div
          style={{ height: "100vh", display: "flex", flexDirection: "column" }}
        >
          <Story />
        </div>
      </PrivateNavigationProvider>
    ),
  ],
  parameters: {
    layout: "fullscreen",
    msw: {
      handlers: [
        mockGetWithResponseData<apiTypes["NavStats"]>("/nav-stats", {
          pending_draft_lots: 984,
          audits: 5,
          doublecount_agreement_pending: 10,
          tickets: 100,
          total_pending_action_for_admin: 10,
          charge_point_registration_pending: 10,
          metering_reading_pending: 10,
          pending_transfer_certificates: 10,
          in_pending_lots: 5,
        }),
      ],
    },
  },
}
type Story = StoryObj<typeof PrivateNavigation>

export default meta

export const AdminLayout: Story = {
  decorators: [
    (Story) => {
      usePrivateNavigation("this is a title")

      return <Story />
    },
  ],
  args: {
    children: (
      <>
        <div style={{ background: "#aba6a6", height: "200px" }}>
          this is the content of my page
        </div>
        <div style={{ background: "#eda7a7", height: "500px" }}>
          other content
        </div>
      </>
    ),
  },
  parameters: {
    msw: {
      handlers: [
        ...(meta.parameters?.msw?.handlers ?? []),
        mockUser(EntityType.Administration),
      ],
    },
  },
}

export const ExternalAdminElec: Story = {
  ...AdminLayout,
  parameters: {
    msw: {
      handlers: [
        ...(meta.parameters?.msw?.handlers ?? []),
        mockUser(EntityType.ExternalAdmin, {
          right: {
            entity: {
              ext_admin_pages: [ExtAdminPagesEnum.ELEC],
            },
          },
        }),
      ],
    },
  },
}

export const ExternalAdminDCA: Story = {
  ...AdminLayout,
  parameters: {
    msw: {
      handlers: [
        ...(meta.parameters?.msw?.handlers ?? []),
        mockUser(EntityType.ExternalAdmin, {
          right: {
            entity: {
              ext_admin_pages: [ExtAdminPagesEnum.DCA],
            },
          },
        }),
      ],
    },
  },
}

export const OperatorLayout: Story = {
  ...AdminLayout,
  parameters: {
    msw: {
      handlers: [
        ...(meta.parameters?.msw?.handlers ?? []),
        mockUser(EntityType.Operator, {
          right: {
            entity: {
              has_elec: true,
              has_saf: true,
              has_stocks: true,
            },
          },
        }),
      ],
    },
  },
}

export const AuditorLayout: Story = {
  ...AdminLayout,
  parameters: {
    msw: {
      handlers: [
        ...(meta.parameters?.msw?.handlers ?? []),
        mockUser(EntityType.Auditor),
      ],
    },
  },
}

export const ProducerLayout: Story = {
  ...AdminLayout,
  parameters: {
    msw: {
      handlers: [
        ...(meta.parameters?.msw?.handlers ?? []),
        mockUser(EntityType.Producer, {
          right: {
            entity: {
              has_stocks: true,
            },
          },
        }),
      ],
    },
  },
}

export const PowerOrHeatProducerLayout: Story = {
  ...AdminLayout,
  parameters: {
    msw: {
      handlers: [
        ...(meta.parameters?.msw?.handlers ?? []),
        mockUser(EntityType.PowerOrHeatProducer),
      ],
    },
    reactRouter: reactRouterParameters({
      location: {
        pathParams: { entityId: "7", year: "2024" },
      },
      routing: {
        path: "/org/:entityId/transactions/:year/drafts",
        handle: "Profile",
      },
    }),
  },
}

export const TraderLayout: Story = {
  ...AdminLayout,
  parameters: {
    msw: {
      handlers: [
        ...(meta.parameters?.msw?.handlers ?? []),
        mockUser(EntityType.Trader),
      ],
    },
  },
}

export const AirlineLayout: Story = {
  ...AdminLayout,
  parameters: {
    msw: {
      handlers: [
        ...(meta.parameters?.msw?.handlers ?? []),
        mockUser(EntityType.Airline),
      ],
    },
  },
}

export const ChargePointOperatorLayout: Story = {
  ...AdminLayout,
  parameters: {
    msw: {
      handlers: [
        ...(meta.parameters?.msw?.handlers ?? []),
        mockUser(EntityType.CPO),
      ],
    },
  },
}
