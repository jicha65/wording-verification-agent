# 📝 Wording Verification Agent - Complete User Guide

## Overview

This is an **automated wording verification agent** that continuously reviews and validates wording in your documentation to ensure linguistic accuracy, consistency, and cultural appropriateness across regions.

**What it does:**
- ✅ Detects spelling errors and typos
- ✅ Checks for grammatical consistency
- ✅ Ensures proper verb tenses and formatting
- ✅ Applies custom rules (e.g., "Not" instead of "Un", "Successfully" instead of "Successful")
- ✅ Automatically fills validation columns in your CSV file
- ✅ Runs on GitHub automatically when you add new words

---

## Quick Start (30 seconds)

1. Add your word to `Wording Criterias-Wording.csv` (at the bottom)
2. Save (Ctrl+S)
3. Commit & Push using VS Code (Ctrl+Shift+G)
4. Wait for GitHub Actions (30-60 seconds)
5. Pull the results back (Ctrl+Shift+G → Pull)
6. Done! See your validation results ✅

---

## Complete Step-by-Step Workflow

### STEP 1: Add Your New Words (in VS Code)

1. **Open the file** in VS Code:
   - `Wording Criterias-Wording.csv` (should already be open)

2. **Go to the end of the file:**
   - Press **Ctrl+End** to jump to the bottom

3. **Add your new line(s) with this format:**
   ```
   Category,Sub Category,Wording,,,
   ```
   
   **Example - add at the very bottom:**
   ```csv
   Status,General Task,Payment Complete,,,
   Toast,Success Toast,Data synced sucessfully,,,
   Status,Availability,Out of Service,,,
   ```

4. **Save the file:**
   - Press **Ctrl+S**
   - You'll see a white dot on the file tab (unsaved indicator)
   - After saving, the dot disappears
   - **Important:** Don't skip this step!

---

### STEP 2: Commit the Changes (Using VS Code UI)

**This saves your changes with a description**

1. **Open Source Control Panel:**
   - Press **Ctrl+Shift+G** on your keyboard
   - OR click the **Git icon** on the left sidebar (looks like a branch)

2. **You'll see the "Changes" section:**
   - Shows: `Wording Criterias-Wording.csv` with an "M" icon
   - This means the file has been Modified

3. **Type your commit message:**
   - Click in the message box (says "Message (Ctrl+Enter to commit)")
   - Type a clear, short message:
     - ✅ Good: `Add payment status words`
     - ✅ Good: `Test new availability statuses`
     - ❌ Bad: `update`
     - ❌ Bad: `blah`

4. **Commit the changes:**
   - Click the **✓ (Commit)** button (above the message box)
   - OR press **Ctrl+Enter**
   - You should see a message: "✓ Committed"

---

### STEP 3: Push to GitHub (Using VS Code UI)

**This uploads your changes to the cloud and triggers the agent**

1. **Look at the top of the Source Control panel:**
   - You should see icons/buttons
   - Look for an **↑ up arrow** icon or **"Publish Branch"** button

2. **Click the ↑ Push button:**
   - This sends your commit to GitHub
   - Wait 3-5 seconds for completion
   - You should see: "✓ Successfully pushed"

---

### STEP 4: Watch the Agent Work on GitHub (Optional but Fun!)

1. **Open your GitHub repository:**
   - Go to: https://github.com/jicha65/wording-verification-agent

2. **Click the "Actions" tab** (top menu)
   - You'll see your workflow running! 🚀
   - Shows your commit message (e.g., "Add payment status words")

3. **Wait 30-60 seconds for completion:**
   - The workflow will show a green ✅ checkmark when done
   - You'll see the workflow ran the Python script, verified your words, and committed results back

---

### STEP 5: Pull the Results Back to Your Computer

**The agent updated the CSV on GitHub, now get those updates locally**

1. **Open Source Control Panel:**
   - Press **Ctrl+Shift+G**

2. **Look for sync options:**
   - You might see: "⇅ 1 behind" (means GitHub has updates)
   - OR click the **...** (three dots) menu → select **"Pull"**
   - OR click the **↓ Pull** button if visible

3. **Wait for the pull to complete:**
   - Should take 2-3 seconds
   - Your CSV file will be updated with agent results

4. **Reload the file in the editor:**
   - Close the file tab
   - Reopen: File → Open → `Wording Criterias-Wording.csv`
   - OR press **Ctrl+Shift+P** → type "Revert" → press Enter
   - Your new words will now show **complete validation data!** ✅

---

## What You'll See in the CSV

After the agent runs, your new entries will be filled like this:

**Before (what you typed):**
```csv
Status,General Task,Payment Complete,,,
```

**After (agent verification):**
```csv
Status,General Task,Payment Complete,Yes,N/A,Clear status term
```

**With issues (agent suggestion):**
```csv
Toast,Success Toast,Data synced sucessfully,No,Data Synced Successfully,Typo: 'sucessfully' → 'Successfully'. Use past participle 'Synced'
```

| Column | Meaning |
|--------|---------|
| Is the word right? | Yes/No - is it correct? |
| If not right, what is suggested | The corrected wording |
| Why suggest this word | Explanation of the issue |

---

## Visual Checklist - Do This Every Time

Copy and paste this checklist to follow:

```
☐ 1. Open Wording Criterias-Wording.csv
☐ 2. Press Ctrl+End (go to bottom)
☐ 3. Add new word(s) in CSV format
☐ 4. Save (Ctrl+S) - wait for white dot to disappear
☐ 5. Press Ctrl+Shift+G (open Source Control)
☐ 6. Type commit message in text box
☐ 7. Click ✓ button (Commit)
☐ 8. Click ↑ button (Push)
☐ 9. Wait 30-60 seconds for GitHub Actions
☐ 10. Press Ctrl+Shift+G (Source Control) again
☐ 11. Click ↓ button (Pull) to get results
☐ 12. Reload CSV file to see validation results
☐ Done! ✅
```

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Forget to Save
**Problem:** You added text but didn't press Ctrl+S
**Result:** Changes won't be committed
**Fix:** Always press **Ctrl+S** before committing

### ❌ Mistake 2: Add Text in Wrong Place
**Problem:** You edited existing rows instead of adding at the bottom
**Result:** Old data gets corrupted
**Fix:** Always use **Ctrl+End** to go to the bottom, then add **new lines only**

### ❌ Mistake 3: Wrong CSV Format
**Problem:** You added: `Status,New Word` (only 2 columns)
**Result:** Agent can't read it properly
**Fix:** Always use format: `Category,SubCategory,Word,,,` (with empty columns)

### ❌ Mistake 4: Forget to Push
**Problem:** You committed locally but didn't push to GitHub
**Result:** Only your computer has the changes, agent doesn't run
**Fix:** Always click the **↑ Push** button after committing

### ❌ Mistake 5: Don't Pull Results
**Problem:** Agent filled in validation, but you didn't pull
**Result:** Your local file still shows empty validation columns
**Fix:** After workflow completes, always pull (**↓**) before opening file

### ❌ Mistake 6: Wrong Commit Message
**Problem:** You typed: `update` or `blah`
**Result:** Can't see what you changed later
**Fix:** Use clear messages like: `Add payment status words` or `Test new availability statuses`

---

## Verification Rules (What the Agent Checks)

### ✅ Rule 1: Use "Successfully" (adverb form)
- ❌ "Save Successful" → ✅ "Saved Successfully"
- ❌ "Export successful" → ✅ "Exported Successfully"
- Why: Grammatically correct past participle + adverb

### ✅ Rule 2: Use "Not" instead of "Un" prefix
- ❌ "Unavailable" → ✅ "Not Available"
- ❌ "Unconfirmed" → ✅ "Not Confirmed"
- Why: Consistency across terminology

### ✅ Rule 3: Consistent Capitalization
- ❌ "save successfully" → ✅ "Saved Successfully"
- Why: Professional appearance

### ✅ Rule 4: Detect Typos
- ❌ "Acitivate" → ✅ "Activate"
- ❌ "sucessfully" → ✅ "Successfully"
- ❌ "Synchronization" → ✅ "Synchronization"

### ✅ Rule 5: Consistent Verb Forms
- ❌ "Executing" vs "Completed" → ✅ Both use consistent tense
- Why: Professional consistency

---

## File Structure

```
.
├── Wording Criterias-Wording.csv       (← Your main CSV to edit)
├── Wording Criterias-Wording_VALIDATED.csv  (Backup with full analysis)
├── wording-verification.py              (Python verification script)
├── README.md                            (This file)
└── .github/
    ├── agents/
    │   └── wording verfication.agent.md (Agent configuration)
    └── workflows/
        └── wording-verification.yml     (GitHub Actions automation)
```

---

## How It Works Behind the Scenes

```
You Add Word → Save → Commit → Push
                                  ↓
                        GitHub receives push
                                  ↓
         GitHub Actions Workflow Triggers Automatically
                                  ↓
              Python Script Runs on GitHub Servers
                    ↓
        • Reads your new words from CSV
        • Checks against all verification rules
        • Fills validation columns
        • Commits results back to GitHub
                                  ↓
                    Results pushed to GitHub
                                  ↓
         You Pull Results to Your Computer
                                  ↓
      Open CSV → See Validation Data Filled In! ✅
```

---

## Frequently Asked Questions

### Q: How long does the agent take to verify?
**A:** Usually 30-60 seconds after you push. You can watch it in GitHub Actions tab.

### Q: Can I add multiple words at once?
**A:** Yes! Add as many rows as you want at the bottom, then commit once.

### Q: What if I make a mistake?
**A:** No problem! Just:
1. Fix the mistake in VS Code
2. Save (Ctrl+S)
3. Commit again with new message
4. Push again

### Q: Do I always need to pull?
**A:** Yes, always pull to get the latest verified data from GitHub.

### Q: Can I edit the validation columns myself?
**A:** Yes, but they'll be overwritten the next time the agent runs. Better to let the agent fill them.

### Q: What if the workflow fails?
**A:** Check GitHub Actions tab to see error details. Usually it's a file format issue. Contact support if confused.

### Q: Can I test locally without pushing to GitHub?
**A:** Yes! Run: `python wording-verification.py "Wording Criterias-Wording.csv"` in terminal. Results show locally.

---

## Quick Reference - Terminal Commands (Advanced)

If you prefer terminal, here are the equivalent commands:

```powershell
# Check status
git status

# Add changes
git add .

# Commit
git commit -m "Your message here"

# Push to GitHub
git push

# Pull from GitHub
git pull

# View recent commits
git log --oneline
```

---

## Support & Troubleshooting

### Problem: Source Control not working
**Solution:** Reload VS Code (Ctrl+Shift+P → reload)

### Problem: Can't find Source Control
**Solution:** Press Ctrl+Shift+G (shortcut) or click Git icon on left sidebar

### Problem: Changes not showing
**Solution:** Close file and reopen (file wasn't saved)

### Problem: Workflow shows error
**Solution:** Go to GitHub Actions tab and click the failed workflow to see error logs

### Problem: File keeps reverting
**Solution:** Make sure to pull before editing, and commit after saving

---

## Summary

Your wording verification agent is now fully operational! 

**The workflow is:**
1. ✅ Add words locally
2. ✅ Save, Commit, Push (via VS Code UI)
3. ✅ Agent runs automatically on GitHub
4. ✅ Pull results back
5. ✅ See validated data ✅

**That's it!** Repeat this process for all new wording entries.

---

## Repository

**GitHub:** https://github.com/jicha65/wording-verification-agent

---

**Last Updated:** February 25, 2026
**Version:** 1.0
**Status:** ✅ Ready to Use
