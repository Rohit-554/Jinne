import { expect, test } from '@playwright/test'

test('chat page loads with companion identity visible and no console errors', async ({ page }) => {
  const consoleErrors: string[] = []
  page.on('console', (msg) => {
    if (msg.type() === 'error') consoleErrors.push(msg.text())
  })
  page.on('pageerror', (err) => consoleErrors.push(err.message))

  await page.goto('/')

  await expect(page.getByRole('heading', { name: 'Mira' })).toBeVisible()
  await expect(page.getByText('Warm, curious, slightly sarcastic')).toBeVisible()
  await expect(page.getByPlaceholder('Message Mira...')).toBeVisible()

  expect(consoleErrors).toEqual([])
})
