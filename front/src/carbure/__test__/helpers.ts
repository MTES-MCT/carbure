import { screen, waitForElementToBeRemoved } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { rest } from "msw"

export async function waitWhileLoading() {
	const loaders = screen.queryAllByTestId("loader")
	if (loaders.length === 0) return
	await waitForElementToBeRemoved(() => screen.queryAllByTestId("loader"), { timeout: 5000 }) // prettier-ignore
}

export function clone(data: any) {
	return JSON.parse(JSON.stringify(data))
}

export const Data = {
	get(key: string) {
		const data = sessionStorage.getItem(key)
		if (data === null) throw new Error(`key "${key}" has no data`)
		return JSON.parse(data)
	},

	set(key: string, value: any) {
		let data
		if (typeof value === "function") {
			data = Data.get(key)
			data = value(data) ?? data
		} else {
			data = value
		}
		const json = JSON.stringify(data)
		sessionStorage.setItem(key, json)
	},
}

export function getField(label: any) {
	const rx = new RegExp(`^${label}`)
	const field = screen
		.getByText(rx)
		.closest("[data-field]")
		?.querySelector("input")
	if (!field) throw new Error(`Cannot find field with label like ${label}`)
	return field
}

export async function uploadFileField(label: string, file?: any) {
	const user = userEvent.setup()
	if (!file) {
		file = new File(["hello"], "hello.png", { type: "image/png" })
	}
	const dcInput = await getField(label)
	await user.upload(dcInput, file)
	return dcInput
}

export function getByTextContent(textContent: string) {
	return screen.getAllByText((content, node) => {
		return content === textContent || node?.textContent === textContent
	})
}

export function findByTextInNode(textContent: string, nodeName: string) {
	return screen.findByText((content, node) => {
		return content === textContent && node?.nodeName === nodeName
	})
}

export function setEntity(nextEntity: any) {
	Data.set("entity", nextEntity)
}

export const mockGetWithResponseData = (url: string, data: any) => {
	return rest.get("/api" + url, (req, res, ctx) => {
		return res(
			ctx.json({
				status: "success",
				data,
			})
		)
	})
}
export const mockPostWithResponseData = (
	url: string,
	data?: any,
	withError = false,
	error?: string
) => {
	return rest.post("/api" + url, (req, res, ctx) => {
		return res(
			withError ? ctx.status(400) : ctx.status(200),
			ctx.json({
				status: withError ? "error" : "success",
				error,
				data,
			})
		)
	})
}
