# Trust Dashboard v12

### Fixes:
- Notes now persist correctly for both trust and individual schools
- Search term no longer resets the dashboard
- All notes use `st.session_state` + `st.form()` for smooth saving

## Run it:
1. Place `National datasheeet.csv` in the folder
2. Run:
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Login with:
- `admin` / `pass123` or `user` / `school2024`