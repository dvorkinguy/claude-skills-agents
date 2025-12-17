- STOP answering in hebrew. ALWAYS use english

---

## 🧠 AGENT MODEL CONFIGURATION (MANDATORY)

**⚠️ CRITICAL: ALL agents MUST use the most advanced model available**

When spawning ANY agent via the Task tool, ALWAYS set:
```
model: "opus"
```

**This applies to ALL agent types:**
- Explore agents
- Debugger agents
- Code review agents
- All specialized agents (react-pro, nextjs-pro, drizzle-specialist, etc.)
- Plan agents
- Any other subagent

**NO EXCEPTIONS.** Never use "sonnet" or "haiku" for agents - always "opus" for maximum capability.

---

## 👥 AUTO-AGENT INVOCATION SYSTEM 👥
**⚠️ CRITICAL BEHAVIOR: BE PROACTIVE WITH AGENTS! ⚠️**

**BEFORE starting ANY task, ASK YOURSELF:**
"Which specialized agent is BEST suited for this?"

### Delegation Rules (MANDATORY)
- **Errors/bugs** → debugger agent (Priority 1)
- **"How/where/what" questions** → Explore agent (Priority 2)
- **Large implementations** → EnterPlanMode (Priority 3)
- **Domain-specific tasks** → Specialized agents (Priority 4)
- **After code changes** → Quality agents automatically (Priority 5)

**Execution Strategy:**
- Launch parallel when tasks are independent
- Launch sequential when outputs inform next inputs
- No user confirmation needed - delegate immediately

**Trust your judgment**: With specialized agents available, delegate rather than handling everything yourself.

### Mental Checklist (Execute Before Every Response)
```
[ ] Parse for trigger keywords (error, how, where, domain terms)
[ ] Identify ALL matching patterns (not just first match)
[ ] Score priorities (1=errors > 2=explore > 3=plan > 4=specialized > 5=quality)
[ ] Check parallel opportunities (multiple independent matches)
[ ] Launch agents automatically OR recognize when to suggest them
[ ] Synthesize results and respond
```

### Pattern Matching Reference

**Error/Debug Triggers (Priority 1):**
- Keywords: error, bug, broken, not working, fails, crash, exception
- HTTP codes: 404, 500, 403, 401
- Stack traces, build/test failures
- Action: Launch `debugger` agent immediately

**Exploration Triggers (Priority 2):**
- Keywords: how does, where is, what handles, why does, when is, which file
- Questions: explain, understand, show me, find where
- Architecture: structure, flow, architecture
- Action: Launch `Explore` agent (quick/medium/thorough)

**Planning Triggers (Priority 3):**
- Keywords: implement, add feature, refactor, migrate
- Decisions: should we, best approach, how to structure
- Complex additions: auth, payments, i18n
- Action: Enter plan mode first

**Specialized Domain Triggers (Priority 4):**
- Database: schema, migration, SQL, Drizzle → `drizzle-specialist`
- React: hooks, useState, useEffect, component → `react-pro`
- Next.js: App Router, Server Action, RSC → `nextjs-pro`
- RTL: Hebrew, Arabic, direction, ps-, pe- → `i18n-rtl`
- Performance: slow, optimize, bundle → `performance-auditor`
- Accessibility: WCAG, a11y, screen reader → `accessibility-checker`
- Security: vulnerability, audit, XSS, OWASP → `security-auditor`

**Code Quality Triggers (Priority 5 - Automatic Post-Change):**
- After ANY code modification → Auto-launch quality agents
- Auth code → `security-auditor`
- UI components → `accessibility-checker`
- Any changes → `test-runner`
- Before commit → `code-reviewer`

---

## 🎭 PLAYWRIGHT VISUAL TESTING (MANDATORY)

**⚠️ CRITICAL: Playwright is the DEFAULT tool for all visual/functional testing**

### When to Use Playwright (AUTOMATIC)

**ALWAYS use Playwright for:**
1. **Visual verification** - "Check if X works", "Test the UI", "Verify functionality"
2. **User flow testing** - "Test the signup flow", "Verify the checkout process"
3. **Regression testing** - After any UI changes or bug fixes
4. **Cross-browser testing** - Desktop, mobile, tablet viewports
5. **Integration testing** - Full stack features (frontend + backend)

**Trigger Keywords:**
- "check", "test", "verify", "validate", "ensure"
- "does it work", "is it working", "can you test"
- "visual testing", "e2e", "integration test"
- User reports issues or unexpected behavior in UI

### Playwright Setup Requirements

**If Playwright is NOT installed:**
1. Auto-install: `npm install -D @playwright/test playwright`
2. Install browsers: `npx playwright install chromium`
3. Create config: `playwright.config.ts` with:
   - baseURL: current dev server
   - testDir: './e2e'
   - Single worker for stability
   - Screenshots on failure

**Test Structure (Standard):**
```typescript
// e2e/feature.spec.ts
test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/route');
  });

  test('should do something', async ({ page }) => {
    // Arrange
    // Act
    // Assert
  });
});
```

### Mandatory Test Coverage

**For ANY frontend work, create tests for:**
1. **Page Load** - Verify page renders without errors
2. **User Interactions** - Click buttons, fill forms, navigate
3. **API Integration** - Check network requests succeed
4. **Error States** - Test error handling and display
5. **Responsive Design** - Mobile (375px), tablet (768px), desktop
6. **Accessibility** - Proper ARIA labels, keyboard navigation
7. **Authentication Flows** - Login/logout if applicable

### Running Tests

**Standard workflow:**
1. Run tests: `npx playwright test --reporter=list`
2. View failures: Check screenshots in `test-results/`
3. Debug: `npx playwright test --debug`
4. UI mode: `npx playwright test --ui`

**Integration with development:**
- Run tests AFTER any UI changes (automatic)
- Run tests BEFORE creating PR (mandatory)
- Run tests AFTER bug fixes (verification)

### Test Reporting

**ALWAYS report:**
- ✅ Number of passed tests
- ❌ Number of failed tests with reasons
- 📸 Screenshot locations for failures
- 🔍 Key findings (what works, what needs fixing)
- 📋 Actionable next steps

### Authentication Handling

**If tests fail due to authentication:**
1. **Option A:** Add test user credentials and login flow
2. **Option B:** Create auth bypass for E2E tests
3. **Option C:** Use Playwright's storage state for session reuse

**Example login flow:**
```typescript
test.beforeEach(async ({ page }) => {
  await page.goto('/login');
  await page.fill('[name="email"]', process.env.TEST_USER_EMAIL);
  await page.fill('[name="password"]', process.env.TEST_USER_PASSWORD);
  await page.click('button[type="submit"]');
  await page.waitForURL('/dashboard');
});
```

### Proactive Testing Protocol

**DO NOT wait for user to request tests. PROACTIVELY:**
1. After implementing new UI feature → Create and run Playwright tests
2. After fixing UI bug → Write regression test
3. After major refactor → Full test suite run
4. Before suggesting "done" → Verify with Playwright

**Example:**
```
User: "Add a login form"
Assistant:
1. Implements login form
2. Creates e2e/login.spec.ts with tests
3. Runs tests automatically
4. Reports: "✅ Login form implemented and tested (5/5 tests passing)"
```

### Selectors Best Practices

**Priority order:**
1. **Role-based:** `getByRole('button', { name: 'Submit' })`
2. **Label-based:** `getByLabel('Email address')`
3. **Placeholder:** `getByPlaceholder('Enter email')`
4. **Text content:** `getByText('Welcome')`
5. **Test IDs:** `getByTestId('login-button')` (last resort)

**NEVER use:**
- CSS class selectors (brittle)
- XPath (hard to maintain)
- nth-child selectors (fragile)

### Screenshot Strategy

**Automatic screenshots for:**
- ❌ Test failures (Playwright default)
- ⚠️ Console errors detected
- 🔄 Before/after state changes

**Comparison testing:**
```typescript
await expect(page).toHaveScreenshot('feature-name.png', {
  maxDiffPixels: 100
});
```

### Performance Testing

**Include performance checks:**
```typescript
test('should load quickly', async ({ page }) => {
  const startTime = Date.now();
  await page.goto('/');
  const loadTime = Date.now() - startTime;

  expect(loadTime).toBeLessThan(3000); // 3s max
});
```

---

### 🚨 CHECKPOINT INTEGRATION

**Add to existing checkpoint:**
```
[AGENT DECISION CHECKPOINT]

1. Task Classification:
   □ Visual/UI testing request → PLAYWRIGHT (MANDATORY)
   □ "Test", "verify", "check" keywords → PLAYWRIGHT (MANDATORY)

[END CHECKPOINT]
```

**Blocking Rule:**
- NEVER say "looks good" or "should work" without Playwright verification
- NEVER mark UI tasks complete without running tests
- NEVER skip testing because "it's simple" - test everything