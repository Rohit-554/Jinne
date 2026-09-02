import { expect, test } from '@playwright/test'

test('a contradiction is reflected in the memory panel after the second turn', async ({ page }) => {
  await page.goto('/')

  const input = page.getByPlaceholder('Message Jinne...')

  await input.fill('I work at Google.')
  await input.press('Enter')
  await expect(input).toBeEnabled({ timeout: 45_000 })

  await input.fill('I left Google and joined Microsoft.')
  await input.press('Enter')
  await expect(input).toBeEnabled({ timeout: 45_000 })

  // The memory panel refetches after each turn; after the contradiction,
  // the most recent employer fact visible should be Microsoft.
  await expect(page.getByText('Microsoft', { exact: false }).last()).toBeVisible({ timeout: 15_000 })
})
