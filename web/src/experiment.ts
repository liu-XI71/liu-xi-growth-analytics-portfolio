export interface ExperimentInputs {
  baseline: number
  mde: number
  alpha: number
  power: number
  dailyTraffic: number
}

function inverseNormal(probability: number) {
  const p = Math.min(1 - 1e-12, Math.max(1e-12, probability))
  const a = [-39.69683028665376, 220.9460984245205, -275.9285104469687, 138.357751867269, -30.66479806614716, 2.506628277459239]
  const b = [-54.47609879822406, 161.5858368580409, -155.6989798598866, 66.80131188771972, -13.28068155288572]
  const c = [-0.007784894002430293, -0.3223964580411365, -2.400758277161838, -2.549732539343734, 4.374664141464968, 2.938163982698783]
  const d = [0.007784695709041462, 0.3224671290700398, 2.445134137142996, 3.754408661907416]
  const low = 0.02425
  const high = 1 - low
  if (p < low) {
    const q = Math.sqrt(-2 * Math.log(p))
    return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
  }
  if (p <= high) {
    const q = p - 0.5
    const r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
  }
  const q = Math.sqrt(-2 * Math.log(1 - p))
  return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
}

export function sampleSizePerArm({ baseline, mde, alpha, power }: ExperimentInputs) {
  const treatment = baseline + mde
  if (![baseline, mde, alpha, power].every(Number.isFinite)) return null
  if (baseline <= 0 || treatment >= 1 || mde <= 0 || alpha <= 0 || alpha >= 1 || power <= 0 || power >= 1) return null
  const pooled = (baseline + treatment) / 2
  const zAlpha = inverseNormal(1 - alpha / 2)
  const zPower = inverseNormal(power)
  const numerator = zAlpha * Math.sqrt(2 * pooled * (1 - pooled)) + zPower * Math.sqrt(baseline * (1 - baseline) + treatment * (1 - treatment))
  return Math.ceil((numerator * numerator) / (mde * mde))
}

export function recommendedDuration(inputs: ExperimentInputs) {
  const perArm = sampleSizePerArm(inputs)
  if (!perArm || !Number.isSafeInteger(inputs.dailyTraffic) || inputs.dailyTraffic <= 0) return null
  const statisticalDays = Math.max(1, Math.ceil((perArm * 2) / inputs.dailyTraffic))
  const fullCycleDays = Math.ceil(statisticalDays / 7) * 7
  return { perArm, total: perArm * 2, statisticalDays, fullCycleDays }
}

export const DEFAULT_HASH_SALT = 'liu_xi_growth_analytics_demo_v1'

export async function stableBucket(unitId: string, salt = DEFAULT_HASH_SALT, buckets = 100) {
  if (!Number.isInteger(buckets) || buckets < 2) throw new Error('buckets must be an integer >= 2')
  const bytes = new TextEncoder().encode(`${salt}:${unitId}`)
  const digest = new Uint8Array(await globalThis.crypto.subtle.digest('SHA-256', bytes))
  let firstEightBytes = 0n
  for (const byte of digest.slice(0, 8)) firstEightBytes = (firstEightBytes << 8n) | BigInt(byte)
  return Number(firstEightBytes % BigInt(buckets))
}

function normalCdf(value: number) {
  const sign = value < 0 ? -1 : 1
  const x = Math.abs(value) / Math.sqrt(2)
  const t = 1 / (1 + 0.3275911 * x)
  const erf = 1 - (((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t) * Math.exp(-x * x)
  return 0.5 * (1 + sign * erf)
}

export function twoProportionTest(controlSuccess: number, controlN: number, treatmentSuccess: number, treatmentN: number) {
  if (![controlSuccess, controlN, treatmentSuccess, treatmentN].every(Number.isSafeInteger)) return null
  if (controlN <= 0 || treatmentN <= 0 || controlSuccess < 0 || treatmentSuccess < 0 || controlSuccess > controlN || treatmentSuccess > treatmentN) return null
  const pControl = controlSuccess / controlN
  const pTreatment = treatmentSuccess / treatmentN
  const pooled = (controlSuccess + treatmentSuccess) / (controlN + treatmentN)
  const standardError = Math.sqrt(pooled * (1 - pooled) * (1 / controlN + 1 / treatmentN))
  if (!standardError) return null
  const z = (pTreatment - pControl) / standardError
  const pValue = 2 * (1 - normalCdf(Math.abs(z)))
  return { pControl, pTreatment, lift: pTreatment - pControl, relativeLift: pControl > 0 ? (pTreatment - pControl) / pControl : null, z, pValue }
}

export function srmCheck(controlN: number, treatmentN: number) {
  if (![controlN, treatmentN].every(Number.isSafeInteger) || controlN < 0 || treatmentN < 0) return null
  const total = controlN + treatmentN
  if (total <= 0) return null
  const expected = total / 2
  const chiSquare = ((controlN - expected) ** 2 + (treatmentN - expected) ** 2) / expected
  const pValue = 2 * (1 - normalCdf(Math.sqrt(chiSquare)))
  return { chiSquare, pValue, passed: pValue >= 0.05 }
}
