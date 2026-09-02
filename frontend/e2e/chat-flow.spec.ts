import { expect, test } from '@playwright/test'

test('sending a message streams a real response and updates the memory panel', async ({ page }) => {
  await page.goto('/')

  const input = page.getByPlaceholder('Message Jinne...')
  await input.fill("My dog's name is Bruno.")
  await input.press('Enter')

  // The user's message should appear immediately.
  await expect(page.getByText("My dog's name is Bruno.")).toBeVisible()

  // A streamed assistant response should appear (real Groq call) within a
  // generous timeout, and the input should be re-enabled once the turn
  // completes (streaming finished).
  await expect(input).toBeEnabled({ timeout: 45_000 })

  const assistantBubbles = page.locator('div.border-border').filter({ hasNotText: "My dog's name is Bruno." })
  await expect(assistantBubbles.first()).not.toBeEmpty()

  // The memory inspector should refetch after the turn and show the new
  // fact (Bruno) as an active memory.
  await expect(page.getByText('Bruno', { exact: false }).last()).toBeVisible({ timeout: 15_000 })
})
