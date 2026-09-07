import { describe, expect, it } from 'vitest'
import vectors from '../../data/contracts/hash_vectors.json'
import { DEFAULT_HASH_SALT, stableBucket } from './experiment'

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
