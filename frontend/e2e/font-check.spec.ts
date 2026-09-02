import { expect, test } from '@playwright/test'

test('body uses Sora and memory-type tags stay JetBrains Mono', async ({ page }) => {
  await page.goto('/')

  const bodyFont = await page.evaluate(() => getComputedStyle(document.body).fontFamily)
  expect(bodyFont).toContain('Sora')

  await expect(page.getByRole('heading', { name: 'Jinne' })).toBeVisible()

  const memoryTag = page.locator('.font-mono').first()
  if (await memoryTag.count()) {
    const tagFont = await memoryTag.evaluate((el) => getComputedStyle(el).fontFamily)
    expect(tagFont).toContain('JetBrains Mono')
  }
})
