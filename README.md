# Trust Dashboard v11

### New Features:
- Per-school notes fields (editable, saved per school using URN)
- Basic user authentication (via sidebar login)
- Trust notes persist as before
- Highlight matching schools with keyword search
- Auto-fix school website links
- CSV and Excel download support

## Run Instructions:
1. Add `National datasheeet.csv` to this folder
2. Run:
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
Login:
- user: `admin` or `user`
- pass: `pass123` or `school2024`