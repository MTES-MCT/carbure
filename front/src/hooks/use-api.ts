import { Reducer, useEffect, useReducer } from "react"
import { ApiResponse } from "../services/api"

enum Status {
  Pending = "pending",
  Error = "error",
  Success = "success",
}

type ApiCaller<T> = (...args: any[]) => ApiResponse<T>

export type ApiState<T> = {
  loading: boolean
  error: string | null
  data: T | null
}

type ApiAction<T> =
  | { type: Status.Pending }
  | { type: Status.Error; payload: string }
  | { type: Status.Success; payload: T }

function reducer<T>(state: ApiState<T>, action: ApiAction<T>): ApiState<T> {
  switch (action.type) {
    case Status.Pending:
      return { loading: true, error: null, data: null }
    case Status.Error:
      return { loading: false, error: action.payload, data: null }
    case Status.Success:
      return { loading: false, error: null, data: action.payload }
    default:
      return state
  }
}

const initialState = {
  loading: false,
  error: null,
  data: null,
}

function useAPI<T>(callAPI: ApiCaller<T>) {
  const [state, dispatch] = useReducer<Reducer<ApiState<T>, ApiAction<T>>>(
    reducer,
    initialState
  )

  async function resolve(...args: any[]) {
    // signal that the request process started
    dispatch({ type: Status.Pending })

    try {
      // actually call the api and wait for the response
      const res = await callAPI(...args)

      if (res.status === "success") {
        dispatch({ type: Status.Success, payload: res.data })
      } else if (res.status === "error" || res.status === "forbidden") {
        dispatch({ type: Status.Error, payload: res.message })
      }

      return res
    } catch (err) {
      dispatch({ type: Status.Error, payload: err.message })
    }

    return null
  }

  function useResolve(...args: any[]) {
    useEffect(() => {
      resolve(...args)
    }, args) // eslint-disable-line react-hooks/exhaustive-deps
  }

  return { ...state, resolve, useResolve }
}

export default useAPI
