import { AccountPlan, Quotas, Feature, Billing } from "./index"

export interface License {
  features: Feature[]
  quotas: Quotas
  plan: AccountPlan
  billing?: Billing
}
