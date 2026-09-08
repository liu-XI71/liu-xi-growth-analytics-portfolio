import { describe, expect, it } from 'vitest'
import vectors from '../../data/contracts/hash_vectors.json'
import { DEFAULT_HASH_SALT, recommendedDuration, sampleSizePerArm, srmCheck, stableBucket, twoProportionTest } from './experiment'

describe('stable SHA-256 assignment contract', () => {
  it.each(vectors.vectors)('matches the shared golden vector for $unit_id', async ({ unit_id, bucket }) => {
    await expect(stableBucket(unit_id, vectors.salt, vectors.buckets)).resolves.toBe(bucket)
  })

  it('is stable and salt-sensitive', async () => {
    await expect(stableBucket('1001')).resolves.toBe(7)
    await expect(stableBucket('1001', DEFAULT_HASH_SALT)).resolves.toBe(7)
    await expect(stableBucket('1001', 'another-experiment')).resolves.not.toBe(40)
  })
})

describe('experiment input validation', () => {
  const defaults = { baseline: 0.17, mde: 0.03, alpha: 0.05, power: 0.8, dailyTraffic: 500000 }
  it('rejects invalid design parameters and non-integer traffic', () => {
    expect(sampleSizePerArm({ ...defaults, baseline: NaN })).toBeNull()
    expect(sampleSizePerArm({ ...defaults, power: Infinity })).toBeNull()
    expect(sampleSizePerArm({ ...defaults, mde: -0.01 })).toBeNull()
    expect(recommendedDuration({ ...defaults, dailyTraffic: -1 })).toBeNull()
    expect(recommendedDuration({ ...defaults, dailyTraffic: 0.5 })).toBeNull()
    expect(recommendedDuration(defaults)?.fullCycleDays).toBe(7)
  })
  it('rejects impossible conversion counts instead of emitting a decision', () => {
    expect(twoProportionTest(101, 100, 50, 100)).toBeNull()
    expect(twoProportionTest(-1, 100, 50, 100)).toBeNull()
    expect(twoProportionTest(1, 100.5, 50, 100)).toBeNull()
    expect(twoProportionTest(1, NaN, 50, 100)).toBeNull()
    expect(twoProportionTest(0, 100, 0, 100)).toBeNull()
  })
  it('allows a valid zero control rate without inventing relative lift', () => {
    const result = twoProportionTest(0, 100, 10, 100)
    expect(result?.lift).toBe(0.1)
    expect(result?.relativeLift).toBeNull()
    expect(result?.pValue).toBeLessThan(0.05)
  })
  it('rejects invalid SRM counts and recognizes a severe mismatch', () => {
    expect(srmCheck(-1, 100)).toBeNull()
    expect(srmCheck(100.5, 100)).toBeNull()
    expect(srmCheck(NaN, 100)).toBeNull()
    expect(srmCheck(100, 100)?.passed).toBe(true)
    expect(srmCheck(10, 1000)?.passed).toBe(false)
  })
})
