import type { Meta, StoryObj } from "@storybook/react"
import { reactRouterParameters } from "storybook-addon-remix-react-router"
import GLOBAL_MOCKS from "@storybook/mocks"
import { getViewport } from "@storybook/mocks/utils"
import { ProvisionCertificateDetails } from "./index"
import {
  okGetProvisionCertificateEnrCompensationDetails,
  okGetProvisionCertificateMeterReadingsDetails,
} from "../../__test__/api"

const meta = {
  title: "modules/elec/pages/certificates/ProvisionCertificateDetails",
  component: ProvisionCertificateDetails,
  parameters: {
    layout: "centered",
    viewport: getViewport("fullModal", { width: "800px", height: "900px" }),
    reactRouter: reactRouterParameters({
      location: {
        pathParams: { id: "1" },
        hash: "#provision-certificate/1",
      },
      routing: {
        path: "/provision-certificate/:id",
      },
    }),
    msw: {
      handlers: [
        ...GLOBAL_MOCKS,
        okGetProvisionCertificateMeterReadingsDetails,
      ],
    },
  },
} satisfies Meta<typeof ProvisionCertificateDetails>

export default meta

type Story = StoryObj<typeof ProvisionCertificateDetails>

export const MeterReadings: Story = {}

export const EnrRatioCompensation: Story = {
  parameters: {
    reactRouter: reactRouterParameters({
      location: {
        pathParams: { id: "2" },
        hash: "#provision-certificate/2",
      },
      routing: {
        path: "/provision-certificate/:id",
      },
    }),
    msw: {
      handlers: [
        ...GLOBAL_MOCKS,
        okGetProvisionCertificateEnrCompensationDetails,
      ],
    },
  },
}
