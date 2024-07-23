import axios from "axios"

const API_ROOT = `${window.location.origin}/api`

export interface Api<T> {
	status: "success" | "error"
	data?: T
	error?: string
}

export const api = axios.create({
	baseURL: API_ROOT,
	paramsSerializer: {
		serialize: (params) => toSearchParams(params).toString(),
	},
	transformRequest: (data) => toFormData(data),
	xsrfCookieName: "csrftoken",
	xsrfHeaderName: "X-CSRFTOKEN",
})

export function download(endpoint: string, params: any) {
	return window.open(API_ROOT + endpoint + "?" + toSearchParams(params))
}

// converts an javascript object into FormData
export function toFormData(obj: any): FormData {
	const formData = new FormData()
	for (const key in obj) {
		if (obj[key] instanceof FileList) {
			Array.from(obj[key]).forEach((value: any) => formData.append(key, value))
		} else if (Array.isArray(obj[key])) {
			obj[key].forEach((value: any) => formData.append(key, value.toString()))
		} else if (!isEmpty(obj[key])) {
			formData.append(key, obj[key])
		}
	}
	return formData
}

export function toSearchParams(params: any) {
	const urlParams = new URLSearchParams()
	for (const key in params) {
		const param = params[key]
		if (Array.isArray(param)) {
			param.forEach((value) => urlParams.append(key, value))
		} else if (!isEmpty(param)) {
			urlParams.append(key, param)
		}
	}
	return urlParams
}

function isEmpty(value: any) {
	const isNull = value === null
	const isUndefined = value === undefined
	const isEmpty = Array.isArray(value) && value.length === 0
	return isNull || isUndefined || isEmpty
}

export default api
