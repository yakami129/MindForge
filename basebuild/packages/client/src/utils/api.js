import { API } from "basebuild/packages/client/src/utils/api"

export const getAPIKey = async () => {
  const { apiKey } = await API.fetchDeveloperInfo()
  return apiKey
}
