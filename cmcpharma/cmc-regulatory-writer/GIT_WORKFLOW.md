# Git Workflow Guide for Safe Development

## Quick Reference Commands

### When User Says "Code is Good and Commit"

Follow this exact sequence:

1. **Check current status**
   ```bash
   git status
   ```

2. **Review changes**
   ```bash
   git diff
   ```

3. **Stage changes**
   ```bash
   git add .
   # OR stage specific files:
   git add filename1 filename2
   ```

4. **Commit with descriptive message**
   ```bash
   git commit -m "fix: [brief description of what was fixed]"
   ```

5. **Verify commit**
   ```bash
   git log --oneline -1
   ```

## Branch Management Workflow

### Starting New Feature/Fix
```bash
# Always start from main branch
git checkout main

# Create new branch for feature/fix
git checkout -b feature-name
# Examples:
# git checkout -b fix-layout
# git checkout -b add-sidebar
# git checkout -b improve-css
```

### Daily Development Cycle
1. **Make small incremental change** (edit 1-2 files max)
2. **Test in browser/application**
3. **If working: commit immediately**
4. **If broken: fix or revert**
5. **Repeat**

### Commit Message Standards
- `fix: [description]` - Bug fixes
- `feat: [description]` - New features
- `style: [description]` - CSS/styling changes
- `refactor: [description]` - Code improvements
- `docs: [description]` - Documentation changes

Examples:
```bash
git commit -m "fix: improve main container flexbox layout"
git commit -m "feat: add responsive design for mobile"
git commit -m "style: update button hover effects"
git commit -m "fix: resolve TypeScript compilation errors"
```

## Emergency Recovery Commands

### If Something Goes Wrong
```bash
# Undo last commit but keep changes
git reset --soft HEAD~1

# Undo last commit and discard changes
git reset --hard HEAD~1

# Go back to previous working state
git reset --hard HEAD~2

# Go back to specific commit
git reset --hard commit-hash
```

### If Need to Revert to Main
```bash
git checkout main
git reset --hard origin/main
```

## File Status Check Commands

### Before Making Changes
```bash
git status              # Check current state
git branch             # Confirm current branch
git log --oneline -5   # See recent commits
```

### After Making Changes
```bash
git status             # See what changed
git diff              # See exact changes
git diff filename     # See changes in specific file
```

## Branch Safety Rules

### Always Follow This Order:
1. **Create branch** before making changes
2. **Make small changes** (1-3 files max)
3. **Test immediately** after each change
4. **Commit working states** frequently
5. **Never accumulate** large untested changes

### Branch Naming Convention:
- `fix-[issue]` - Bug fixes
- `feat-[feature]` - New features
- `improve-[component]` - Improvements
- `refactor-[component]` - Code refactoring

Examples:
- `fix-layout-issues`
- `feat-suggest-edits-panel`
- `improve-responsive-design`
- `refactor-css-styles`

## Testing Workflow

### After Each Change:
1. **Start dev server** (if not running)
   ```bash
   cd frontend && npm run dev
   ```

2. **Check browser** at `http://localhost:5173` (or assigned port)

3. **Test functionality** that was changed

4. **If working**: proceed to commit

5. **If broken**: fix immediately or revert

### Build Testing (Before Major Commits)
```bash
# Test frontend build
cd frontend && npm run build

# If build fails, fix errors before committing
```

## Commit Workflow Steps

### Step 1: Pre-Commit Check
```bash
git status
git diff
```

### Step 2: Stage Changes
```bash
# Stage all changes
git add .

# OR stage specific files
git add frontend/src/styles/regulatory.css
git add frontend/src/components/Layout/RightPanel.tsx
```

### Step 3: Commit
```bash
git commit -m "fix: improve right panel layout positioning"
```

### Step 4: Verify
```bash
git log --oneline -1
git status
```

## Advanced Recovery Options

### If Multiple Commits Need to be Undone
```bash
# See commit history
git log --oneline -10

# Reset to specific commit
git reset --hard commit-hash

# Or reset by number of commits
git reset --hard HEAD~3  # Go back 3 commits
```

### If Need to Keep Some Changes
```bash
# Soft reset (keeps changes in working directory)
git reset --soft HEAD~1

# Mixed reset (keeps changes but unstages them)
git reset HEAD~1

# Hard reset (discards all changes)
git reset --hard HEAD~1
```

## Integration with Main Branch

### When Feature is Complete
```bash
# Switch to main
git checkout main

# Merge feature branch
git merge feature-branch-name

# Delete feature branch
git branch -d feature-branch-name
```

### Or Create Pull Request (if using GitHub)
```bash
# Push feature branch
git push -u origin feature-branch-name

# Then create PR through GitHub interface
```

## Daily Best Practices

1. **Always start** with `git status` and `git branch`
2. **Make small changes** - edit 1-2 files maximum
3. **Test immediately** after each change
4. **Commit frequently** - don't wait for perfection
5. **Use clear commit messages** - explain what and why
6. **Keep branches focused** - one feature/fix per branch
7. **Clean up branches** - delete merged branches

## Emergency Contacts

### If Everything is Broken
```bash
# Go back to last known working state
git checkout main
git reset --hard origin/main

# Or go back to specific working commit
git reset --hard commit-hash
```

### If Need to Start Over
```bash
# Stash current changes
git stash

# Go back to clean main
git checkout main
git reset --hard origin/main

# Create new branch
git checkout -b new-attempt
```

---

**Remember**: Small changes, frequent commits, test everything!

**When in doubt**: commit current working state before trying anything new.

**Golden Rule**: If it works, commit it immediately!
