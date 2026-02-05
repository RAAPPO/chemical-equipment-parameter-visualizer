# 🔴 EMERGENCY ROLLBACK PROCEDURE

If anything breaks:

```bash
# 1. Switch back to main branch
git checkout main

# 2. Discard all changes
git reset --hard HEAD

# 3. Restart servers
cd backend && python manage.py runserver 8100 &
cd frontend-web && npm run dev &
cd frontend-desktop && python main.py