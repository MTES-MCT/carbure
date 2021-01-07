import { setupServer } from "msw/node"
import { okSettings } from "settings/__test__/api"
import { okLots, okSnapshot } from "transactions/__test__/api"

export default setupServer(okSettings, okSnapshot, okLots)
