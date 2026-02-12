# Step 3.5 Flash + Roo Code Integration Guide

Configure **Step 3.5 Flash** as the backend for **[Roo Code](https://roocode.com/)** (VS Code extension) to enable a powerful, autonomous pair-programming experience.

## 1. Why Step 3.5 Flash + Roo Code?

-   **Deep Reasoning:** Flash understands complex project structures and multi-step instructions.
-   **256K Context:** Process entire codebases for holistic refactoring.
-   **Speed:** fast response times minimize waiting during iterative loops.

## 2. Prerequisites

1.  **API Key:** Get yours from the [StepFun Platform](https://platform.stepfun.com/) (or [OpenRouter](https://openrouter.ai)).
2.  **Extension:** Install `Roo Code` from the [VS Code Marketplace](https://marketplace.visualstudio.com/).

## 3. Configuration

Open Roo Code settings (Gear icon) and configure:

### 3.1 Connection
-   **API Provider:** `OpenAI Compatible`
-   **Base URL:**
    -   StepFun (International): `https://api.stepfun.ai/v1`
    -   StepFun (China): `https://api.stepfun.com/v1`
    -   OpenRouter: `https://openrouter.ai/api/v1`
-   **API Key:** Enter your key.
-   **Model ID:** (`stepfun/`)`step-3.5-flash`

### 3.2 Parameters
-   **Context Window:** `256000` (Crucial for large projects)
-   **Max Output Token:** `-1` (Let server decide)
-   **Stream:** Enabled

## 4. Best Practices

-   **Auto-Approve:** Enable for low-risk actions to speed up workflows.
-   **ASK first:** Use "ASK" mode to plan complex changes before switching to "CODE" mode.
-   **Decompose:** Break large tasks into smaller sub-tasks to leverage Flash's reasoning.
-   **Context Management:** Use `@` mentions to include only relevant files, keeping context focused.
